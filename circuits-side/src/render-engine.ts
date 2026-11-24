/** Viewport culling, bounded SVG caching, and retained DOM reconciliation. */
namespace CircuitRendering {
  const SVG_NS = "http://www.w3.org/2000/svg";
  type Rect = Workbench.ViewRect;
  type Point = { x: number; y: number };

  export interface RenderFrame {
    items: Array<{ id: string; markup: string }>;
    total: number;
    visible: number;
    generated: number;
  }

  /** Inclusive edges avoid disappearing strokes on fractional camera positions. */
  export function intersects(a: Rect, b: Rect): boolean {
    return a.x1 <= b.x2 && a.x2 >= b.x1 && a.y1 <= b.y2 && a.y2 >= b.y1;
  }

  function expand(rect: Rect, amount: number): Rect {
    return { x1: rect.x1 - amount, y1: rect.y1 - amount,
      x2: rect.x2 + amount, y2: rect.y2 + amount };
  }

  /** Slab clipping also supports diagonal segments if a future renderer uses them. */
  function segmentIntersects(a: Point, b: Point, rect: Rect): boolean {
    let enter = 0, exit = 1;
    for (const [start, delta, min, max] of [
      [a.x, b.x - a.x, rect.x1, rect.x2],
      [a.y, b.y - a.y, rect.y1, rect.y2],
    ]) {
      if (delta === 0) {
        if (start < min || start > max) return false;
      } else {
        const first = (min - start) / delta, last = (max - start) / delta;
        enter = Math.max(enter, Math.min(first, last));
        exit = Math.min(exit, Math.max(first, last));
        if (enter > exit) return false;
      }
    }
    return true;
  }

  export function pathIntersects(path: readonly Point[], view: Rect): boolean {
    if (path.length === 1) {
      const p = path[0];
      return p.x >= view.x1 && p.x <= view.x2 && p.y >= view.y1 && p.y <= view.y2;
    }
    for (let i = 1; i < path.length; i++) {
      if (segmentIntersects(path[i - 1], path[i], view)) return true;
    }
    return false;
  }

  function visible(item: Workbench.RenderItem, view?: Rect): boolean {
    if (!view) return true;
    if (!intersects(item.bounds, view)) return false;
    // Account for wire stroke width while checking actual segments, not just the
    // much larger rectangle enclosing a wire that loops around other cards.
    return !item.path || pathIntersects(item.path, expand(view, 2));
  }

  /** Camera movement never changes an item's content version. */
  export class SceneRenderer {
    private cache = new Map<string, { version: string; markup: string }>();
    private characters = 0;

    constructor(private readonly maxEntries = 128, private readonly maxCharacters = 2_000_000) {
      if (!Number.isInteger(maxEntries) || maxEntries < 0 || !Number.isFinite(maxCharacters) || maxCharacters < 0) {
        throw new Error("Render cache budgets must be finite and non-negative");
      }
    }

    clear(): void {
      this.cache.clear();
      this.characters = 0;
    }

    frame(scene: Workbench.RenderScene, view?: Rect, pixelScale = 1, overscanPx = 0): RenderFrame {
      if (!Number.isFinite(pixelScale) || pixelScale <= 0 || !Number.isFinite(overscanPx) || overscanPx < 0) {
        throw new Error("Viewport scale must be positive and overscan non-negative");
      }
      if (view && (!Object.values(view).every(Number.isFinite) || view.x2 < view.x1 || view.y2 < view.y1)) {
        throw new Error("Viewport must have finite, ordered bounds");
      }
      const viewport = view && expand(view, overscanPx / pixelScale);
      const result: RenderFrame = { items: [], total: scene.items.length, visible: 0, generated: 0 };
      const ids = new Set<string>();
      for (const item of scene.items) {
        if (ids.has(item.id)) throw new Error(`Duplicate render item: ${item.id}`);
        ids.add(item.id);
        if (!visible(item, viewport)) continue;
        let entry = this.cache.get(item.id);
        if (!entry || entry.version !== item.version) {
          const markup = item.render();
          result.generated++;
          if (entry) {
            this.characters -= entry.markup.length;
            this.cache.delete(item.id);
          }
          entry = { version: item.version, markup };
          if (this.maxEntries > 0 && markup.length <= this.maxCharacters) {
            this.cache.set(item.id, entry);
            this.characters += markup.length;
          }
        } else {
          // Map insertion order is the LRU list. Touch only visible entries.
          this.cache.delete(item.id);
          this.cache.set(item.id, entry);
        }
        result.items.push({ id: item.id, markup: entry.markup });
        while (this.cache.size > this.maxEntries || this.characters > this.maxCharacters) {
          const oldest = this.cache.keys().next().value;
          if (oldest === undefined) break;
          this.characters -= this.cache.get(oldest)!.markup.length;
          this.cache.delete(oldest);
        }
      }
      // Deleted scene objects must not hold cache memory indefinitely.
      for (const [id, entry] of this.cache) {
        if (!ids.has(id)) { this.characters -= entry.markup.length; this.cache.delete(id); }
      }
      result.visible = result.items.length;
      return result;
    }
  }

  /** Full SVG export remains available independently of the interactive viewport. */
  export function renderScene(scene: Workbench.RenderScene, view?: Rect): string {
    return `<defs>${scene.defs}</defs>` + scene.items.filter(item => visible(item, view)).map(item => item.render()).join("");
  }

  /** Only entering or changed objects mutate DOM; off-screen objects are detached. */
  export class SvgViewportRenderer {
    private readonly cache = new SceneRenderer();
    private readonly defs: SVGDefsElement;
    private defsMarkup = "";
    private readonly mounted = new Map<string, { element: SVGGElement; markup: string }>();

    constructor(private readonly host: SVGGElement) {
      this.defs = host.ownerDocument.createElementNS(SVG_NS, "defs");
      host.replaceChildren(this.defs);
    }

    update(scene: Workbench.RenderScene, view: Rect, pixelScale: number): RenderFrame {
      const frame = this.cache.frame(scene, view, pixelScale, 64);
      if (this.defsMarkup !== scene.defs) {
        this.defs.innerHTML = scene.defs;
        this.defsMarkup = scene.defs;
      }
      const visibleIds = new Set(frame.items.map(item => item.id));
      for (const [id, mounted] of this.mounted) {
        if (visibleIds.has(id)) continue;
        if (mounted.element.contains(this.host.ownerDocument.activeElement)) {
          this.host.closest<HTMLElement>('[tabindex="0"]')?.focus({ preventScroll: true });
        }
        mounted.element.remove();
        this.mounted.delete(id);
      }
      let cursor: ChildNode | null = this.defs.nextSibling;
      let updated = 0;
      for (const item of frame.items) {
        let mounted = this.mounted.get(item.id);
        if (!mounted) {
          const element = this.host.ownerDocument.createElementNS(SVG_NS, "g");
          element.setAttribute("data-render-item", item.id);
          mounted = { element, markup: "" };
          this.mounted.set(item.id, mounted);
        }
        if (mounted.markup !== item.markup) {
          const focusedNode = mounted.element.contains(this.host.ownerDocument.activeElement)
            ? this.host.ownerDocument.activeElement?.getAttribute("data-node") : null;
          mounted.element.innerHTML = item.markup;
          mounted.markup = item.markup;
          // Selection or CPU changes must not lose keyboard focus within a card.
          if (focusedNode) mounted.element.querySelector<SVGElement>("[data-node]")?.focus();
          updated++;
        }
        if (mounted.element !== cursor) this.host.insertBefore(mounted.element, cursor);
        cursor = mounted.element.nextSibling;
      }
      // Read-only diagnostics for regression checks, without adding product UI.
      this.host.dataset.renderTotal = String(frame.total);
      this.host.dataset.renderVisible = String(frame.visible);
      this.host.dataset.renderGenerated = String(frame.generated);
      this.host.dataset.renderUpdated = String(updated);
      return frame;
    }

    dispose(): void {
      this.cache.clear();
      this.mounted.clear();
      this.host.replaceChildren();
    }
  }
}

interface Window { CircuitRendering: typeof CircuitRendering }
window.CircuitRendering = CircuitRendering;
