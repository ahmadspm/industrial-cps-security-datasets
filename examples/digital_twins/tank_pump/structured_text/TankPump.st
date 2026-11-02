(* IEC 61131-3 Structured Text. Invoke once per declared control scan. *)
FUNCTION_BLOCK TankPumpController
VAR_INPUT
    MeasuredLevel : REAL;
    Enabled : BOOL;
    Fresh : BOOL;
    Reset : BOOL;
    LowLevel : REAL := 0.30;
    HighLevel : REAL := 0.70;
    HighTrip : REAL := 0.95;
END_VAR
VAR_OUTPUT
    PumpOn : BOOL := FALSE;
    FaultLatched : BOOL := FALSE;
END_VAR
IF (LowLevel < 0.0) OR (LowLevel >= HighLevel) OR (HighLevel >= HighTrip)
   OR (NOT Fresh) OR (MeasuredLevel >= HighTrip) THEN
    FaultLatched := TRUE;
    PumpOn := FALSE;
ELSIF FaultLatched AND (NOT Reset) THEN
    PumpOn := FALSE;
ELSE
    FaultLatched := FALSE;
    IF NOT Enabled THEN
        PumpOn := FALSE;
    ELSIF MeasuredLevel <= LowLevel THEN
        PumpOn := TRUE;
    ELSIF MeasuredLevel >= HighLevel THEN
        PumpOn := FALSE;
    END_IF;
    (* Deadband retains PumpOn from the preceding scan. *)
END_IF;
END_FUNCTION_BLOCK

FUNCTION_BLOCK TankPumpSimulation
VAR_INPUT
    Enabled : BOOL := TRUE;
    Fresh : BOOL := TRUE;
    Reset : BOOL := FALSE;
    SensorBias : REAL := 0.0;
    SamplePeriod : REAL := 0.1;
    Area : REAL := 1.0;
    Inflow : REAL := 0.05;
    Outflow : REAL := 0.02;
END_VAR
VAR_OUTPUT
    Level : REAL := 0.50;
    MeasuredLevel : REAL;
    PumpOn : BOOL;
    FaultLatched : BOOL;
    ParameterError : BOOL;
END_VAR
VAR
    C : TankPumpController;
    FlowIn : REAL;
END_VAR
ParameterError := (SamplePeriod <= 0.0) OR (Area <= 0.0)
                  OR (Inflow <= Outflow) OR (Outflow < 0.0);
MeasuredLevel := Level + SensorBias;
C(MeasuredLevel := MeasuredLevel, Enabled := Enabled,
  Fresh := Fresh AND (NOT ParameterError), Reset := Reset);
PumpOn := C.PumpOn;
FaultLatched := C.FaultLatched;
IF NOT ParameterError THEN
    IF PumpOn THEN FlowIn := Inflow; ELSE FlowIn := 0.0; END_IF;
    Level := Level + SamplePeriod * (FlowIn - Outflow) / Area;
END_IF;
(* MeasuredLevel is the scan-start observation; Level is the next-step value. *)
END_FUNCTION_BLOCK
