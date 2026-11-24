/// <reference path="types.ts" />

namespace LogicDraw {
  export interface RoutingRect { x: number; y: number; w: number; h: number; id?: string; }
  export interface RoutingOptions {
    obstacles?: readonly RoutingRect[];
    bounds?: RoutingRect;
    clearance?: number;
    stub?: number;
    bendCost?: number;
    avoidParallel?: boolean;
  }
  export interface RouteOptions extends RoutingOptions { net?: string; }
  export interface RoutedConnection { points: RoutePoint[]; net: string; }

  export class RoutingError extends Error {
    constructor(message: string) { super(message); this.name = "RoutingError"; }
  }

  const samePoint = (a: RoutePoint, b: RoutePoint) => a.x === b.x && a.y === b.y;
  const inside = (p: RoutePoint, r: RoutingRect) =>
    p.x > r.x && p.x < r.x + r.w && p.y > r.y && p.y < r.y + r.h;
  const contained = (p: RoutePoint, r: RoutingRect) =>
    p.x >= r.x && p.x <= r.x + r.w && p.y >= r.y && p.y <= r.y + r.h;
  const inflate = (r: RoutingRect, gap: number): RoutingRect =>
    ({ x: r.x - gap, y: r.y - gap, w: r.w + gap * 2, h: r.h + gap * 2, id: r.id });

  /** Strict interior intersection: following an inflated edge preserves clearance. */
  export function segmentHitsRect(a: RoutePoint, b: RoutePoint, r: RoutingRect): boolean {
    if (a.y === b.y) return a.y > r.y && a.y < r.y + r.h &&
      Math.max(a.x, b.x) > r.x && Math.min(a.x, b.x) < r.x + r.w;
    if (a.x === b.x) return a.x > r.x && a.x < r.x + r.w &&
      Math.max(a.y, b.y) > r.y && Math.min(a.y, b.y) < r.y + r.h;
    throw new RoutingError("Wire segments must be orthogonal.");
  }

  export function simplifyRoute(points: readonly RoutePoint[]): RoutePoint[] {
    const result: RoutePoint[] = [];
    for (const point of points) {
      if (result.length && samePoint(result[result.length - 1], point)) continue;
      while (result.length >= 2) {
        const a = result[result.length - 2], b = result[result.length - 1];
        // Preserve reversals: they are not redundant collinear points.
        if ((a.x === b.x && b.x === point.x && (b.y - a.y) * (point.y - b.y) >= 0) ||
            (a.y === b.y && b.y === point.y && (b.x - a.x) * (point.x - b.x) >= 0)) result.pop();
        else break;
      }
      result.push({ x: point.x, y: point.y });
    }
    return result;
  }

  export function routePath(points: readonly RoutePoint[]): string {
    return points.map((point, i) => i === 0 ? `M${point.x} ${point.y}` :
      points[i - 1].y === point.y ? `H${point.x}` : `V${point.y}`).join("");
  }

  interface SearchEntry { id: number; cost: number; rank: number; }
  class RouteHeap {
    private entries: SearchEntry[] = [];
    private before(a: SearchEntry, b: SearchEntry): boolean {
      return a.rank < b.rank || (a.rank === b.rank && a.id < b.id);
    }
    push(entry: SearchEntry): void {
      let i = this.entries.length;
      this.entries.push(entry);
      while (i > 0) {
        const parent = (i - 1) >> 1;
        if (!this.before(entry, this.entries[parent])) break;
        this.entries[i] = this.entries[parent]; i = parent;
      }
      this.entries[i] = entry;
    }
    pop(): SearchEntry | undefined {
      const first = this.entries[0], tail = this.entries.pop();
      if (!tail || !this.entries.length) return first;
      let i = 0;
      while (i * 2 + 1 < this.entries.length) {
        let child = i * 2 + 1;
        if (child + 1 < this.entries.length && this.before(this.entries[child + 1], this.entries[child])) child++;
        if (!this.before(this.entries[child], tail)) break;
        this.entries[i] = this.entries[child]; i = child;
      }
      this.entries[i] = tail;
      return first;
    }
  }

  function parallelConflict(a: RoutePoint, b: RoutePoint, c: RoutePoint, d: RoutePoint, gap: number): boolean {
    if (a.y === b.y && c.y === d.y) return Math.abs(a.y - c.y) < gap &&
      Math.max(Math.min(a.x, b.x), Math.min(c.x, d.x)) < Math.min(Math.max(a.x, b.x), Math.max(c.x, d.x));
    if (a.x === b.x && c.x === d.x) return Math.abs(a.x - c.x) < gap &&
      Math.max(Math.min(a.y, b.y), Math.min(c.y, d.y)) < Math.min(Math.max(a.y, b.y), Math.max(c.y, d.y));
    return false;
  }

  /** Visibility-grid A*: node coordinates come from obstacle edges, never pixel rounding. */
  export function orthogonalRoute(
    source: RoutePoint, target: RoutePoint, options: RouteOptions = {},
    previous: readonly RoutedConnection[] = []
  ): RoutePoint[] {
    const clearance = options.clearance ?? 6;
    const requestedStub = options.stub ?? 8;
    const stub = Math.max(requestedStub, clearance);
    const bendCost = options.bendCost ?? 8;
    if (![clearance, requestedStub, bendCost].every(Number.isFinite) || clearance < 0 || requestedStub < 0 || bendCost < 0) {
      throw new RoutingError("Routing clearance, stubs and bend costs must be finite and nonnegative.");
    }
    const bodies = options.obstacles ?? [];
    const rectangles = options.bounds ? [...bodies, options.bounds] : bodies;
    if (rectangles.some(r => ![r.x, r.y, r.w, r.h].every(Number.isFinite) || r.w < 0 || r.h < 0)) {
      throw new RoutingError("Routing rectangles must have finite coordinates and nonnegative dimensions.");
    }
    if (![source.x, source.y, target.x, target.y].every(Number.isFinite)) throw new RoutingError("Invalid pin coordinates.");
    if (samePoint(source, target)) throw new RoutingError("A wire requires distinct endpoint coordinates.");
    if ([source.dir, target.dir].some(dir => dir !== undefined && !["L", "R", "T", "B"].includes(dir))) {
      throw new RoutingError("Invalid pin direction.");
    }
    const obstacles = bodies.map(r => inflate(r, clearance));
    const reserved = options.avoidParallel === false ? [] : previous.filter(r => !options.net || r.net !== options.net);
    const validPoint = (p: RoutePoint) => (!options.bounds || contained(p, options.bounds)) && !obstacles.some(r => inside(p, r));
    const clearSegment = (a: RoutePoint, b: RoutePoint, ignored = -1) =>
      (a.x === b.x || a.y === b.y) &&
      (!options.bounds || (contained(a, options.bounds) && contained(b, options.bounds))) &&
      !obstacles.some((r, i) => i !== ignored && segmentHitsRect(a, b, r)) &&
      !reserved.some(route => route.points.some((p, i) => i > 0 && parallelConflict(a, b, route.points[i - 1], p, clearance)));

    // A pin may lie on a shaped component inside its rectangular envelope. Its
    // only permitted traversal of that envelope is the outward, straight stub.
    const escape = (pin: RoutePoint): RoutePoint => {
      if (!pin.dir) {
        if (!validPoint(pin)) throw new RoutingError("An undirected endpoint lies inside an obstacle or outside the canvas.");
        return { x: pin.x, y: pin.y };
      }
      // Board ports may identify their owner by name; component pins hold the
      // component itself. Neither form may accidentally waive another body.
      const owner = "owner" in pin ? (pin as RoutePoint & { owner?: IComponent | string }).owner : undefined;
      const ownerId = typeof owner === "string" ? owner : owner?.id;
      const index = bodies.findIndex(r => ownerId ? r.id === ownerId : contained(pin, r));
      const body = index < 0 ? undefined : bodies[index];
      if (body && !contained(pin, body)) throw new RoutingError("A pin lies outside its owner's bounds.");
      const point = { x: pin.x, y: pin.y };
      if (pin.dir === "L") point.x = Math.min(pin.x - stub, body ? body.x - clearance : pin.x - stub);
      if (pin.dir === "R") point.x = Math.max(pin.x + stub, body ? body.x + body.w + clearance : pin.x + stub);
      if (pin.dir === "T") point.y = Math.min(pin.y - stub, body ? body.y - clearance : pin.y - stub);
      if (pin.dir === "B") point.y = Math.max(pin.y + stub, body ? body.y + body.h + clearance : pin.y + stub);
      if (!validPoint(point) || !clearSegment(pin, point, index)) {
        throw new RoutingError(`Pin (${pin.x}, ${pin.y}, ${pin.dir}) has no clear outward escape; move components or enlarge the canvas.`);
      }
      return point;
    };
    const start = escape(source), finish = escape(target);
    const hints: RoutePoint[] = (options.waypoints ?? []).map(p => Array.isArray(p) ? { x: p[0], y: p[1] } : p);
    if (!hints.length && (options.viaX !== undefined || options.midX !== undefined)) {
      const x = options.viaX ?? options.midX!;
      hints.push({ x, y: start.y }, { x, y: finish.y });
    } else if (!hints.length && options.viaY !== undefined) {
      hints.push({ x: start.x, y: options.viaY }, { x: finish.x, y: options.viaY });
    }
    if (hints.some(p => !Number.isFinite(p.x) || !Number.isFinite(p.y) || !validPoint(p))) {
      throw new RoutingError("A routing waypoint is obstructed or outside the canvas.");
    }
    const checkpoints = [start, ...hints, finish];
    const xs = new Set(checkpoints.map(p => p.x)), ys = new Set(checkpoints.map(p => p.y));
    obstacles.forEach(r => { xs.add(r.x); xs.add(r.x + r.w); ys.add(r.y); ys.add(r.y + r.h); });
    reserved.forEach(route => route.points.forEach(p => {
      xs.add(p.x - clearance); xs.add(p.x + clearance);
      ys.add(p.y - clearance); ys.add(p.y + clearance);
    }));
    if (options.bounds) {
      xs.add(options.bounds.x); xs.add(options.bounds.x + options.bounds.w);
      ys.add(options.bounds.y); ys.add(options.bounds.y + options.bounds.h);
    } else {
      // Supply exterior tracks even when there are no component obstacles.
      xs.add(Math.min(source.x, target.x) - stub); xs.add(Math.max(source.x, target.x) + stub);
      ys.add(Math.min(source.y, target.y) - stub); ys.add(Math.max(source.y, target.y) + stub);
    }
    const xAxis = [...xs].sort((a, b) => a - b), yAxis = [...ys].sort((a, b) => a - b);
    const columns = xAxis.length, count = columns * yAxis.length;
    const pointAt = (id: number): RoutePoint => ({ x: xAxis[id % columns], y: yAxis[Math.floor(id / columns)] });
    const pointId = (p: RoutePoint) => yAxis.indexOf(p.y) * columns + xAxis.indexOf(p.x);
    const find = (from: RoutePoint, to: RoutePoint): RoutePoint[] => {
      if (samePoint(from, to)) return [from];
      const initial = pointId(from), destination = pointId(to);
      const distance = new Map<number, number>([[initial, 0]]);
      const predecessor = new Map<number, number>();
      const queue = new RouteHeap();
      queue.push({ id: initial, cost: 0, rank: 0 });
      let current: SearchEntry | undefined;
      while ((current = queue.pop())) {
        if (current.cost !== distance.get(current.id)) continue;
        const cell = current.id % count, heading = Math.floor(current.id / count);
        if (cell === destination) {
          const result = [pointAt(cell)];
          let id = current.id;
          while (predecessor.has(id)) { id = predecessor.get(id)!; result.push(pointAt(id % count)); }
          return result.reverse();
        }
        const point = pointAt(cell), col = cell % columns, row = Math.floor(cell / columns);
        const candidates = [col > 0 ? cell - 1 : -1, col + 1 < columns ? cell + 1 : -1,
          row > 0 ? cell - columns : -1, row + 1 < yAxis.length ? cell + columns : -1];
        for (const neighbor of candidates) {
          if (neighbor < 0) continue;
          const next = pointAt(neighbor);
          if (!validPoint(next) || !clearSegment(point, next)) continue;
          const direction = point.y === next.y ? 1 : 2;
          const id = neighbor + direction * count;
          const cost = current.cost + Math.abs(next.x - point.x) + Math.abs(next.y - point.y) +
            (heading && heading !== direction ? bendCost : 0);
          if (cost >= (distance.get(id) ?? Infinity)) continue;
          distance.set(id, cost); predecessor.set(id, current.id);
          queue.push({ id, cost, rank: cost + Math.abs(to.x - next.x) + Math.abs(to.y - next.y) });
        }
      }
      throw new RoutingError("No orthogonal route fits the available space and clearance.");
    };
    const points: RoutePoint[] = [source];
    for (let i = 1; i < checkpoints.length; i++) points.push(...find(checkpoints[i - 1], checkpoints[i]));
    points.push(target);
    return simplifyRoute(points);
  }
}
