/// <reference path="../types.ts" />
/// <reference path="../primitives.ts" />
/// <reference path="../engine.ts" />
/**
 * Intel 8086 Circuit Atlas - Microarchitecture & Subsystem Electrical Logic Modules
 *
 * NOTE: All 31 microarchitecture and subsystem units have been fully modularized
 * into dedicated modules under circuits-side/src/modules/:
 *   - modules/registers.ts (Register File)
 *   - modules/alu.ts       (Arithmetic Logic Unit & CLA)
 *   - modules/flags.ts     (Status & Control Flags Register)
 *   - modules/biu.ts       (Bus Interface Unit - 10 units)
 *   - modules/eu.ts        (Execution Unit - 4 units)
 *   - modules/cu.ts        (Control Unit - 11 units)
 *   - modules/sys.ts       (System Hardware Board - 6 units)
 */
namespace LogicDraw {
  // All legacy implementations decommissioned and modularized into sys.ts.
}
