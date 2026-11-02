(* Add TankPump.st first. Run this program once per PLC scan.
   Inspect Done and AllPassed after twelve scans; no hardware I/O is used. *)
PROGRAM ControllerChecks
VAR
    C : TankPumpController;
    StepIndex : INT := 1;
    Done : BOOL := FALSE;
    AllPassed : BOOL := TRUE;
    MeasuredLevel : REAL;
    Enabled : BOOL;
    Fresh : BOOL;
    Reset : BOOL;
    ExpectedPump : BOOL;
    ExpectedFault : BOOL;
END_VAR
IF NOT Done THEN
    MeasuredLevel := 0.50; Enabled := TRUE; Fresh := TRUE; Reset := FALSE;
    ExpectedPump := FALSE; ExpectedFault := FALSE;
    CASE StepIndex OF
      1: MeasuredLevel := 0.50;
      2: MeasuredLevel := 0.30; ExpectedPump := TRUE;
      3: MeasuredLevel := 0.50; ExpectedPump := TRUE;
      4: MeasuredLevel := 0.70;
      5: MeasuredLevel := 0.20; Enabled := FALSE;
      6: MeasuredLevel := 0.20; ExpectedPump := TRUE;
      7: MeasuredLevel := 0.20; Fresh := FALSE; ExpectedFault := TRUE;
      8: MeasuredLevel := 0.20; ExpectedFault := TRUE;
      9: MeasuredLevel := 0.20; Reset := TRUE; ExpectedPump := TRUE;
     10: MeasuredLevel := 0.95; ExpectedFault := TRUE;
     11: MeasuredLevel := 0.95; Reset := TRUE; ExpectedFault := TRUE;
     12: MeasuredLevel := 0.50; Reset := TRUE;
    END_CASE;
    C(MeasuredLevel := MeasuredLevel, Enabled := Enabled, Fresh := Fresh, Reset := Reset);
    AllPassed := AllPassed AND (C.PumpOn = ExpectedPump)
                           AND (C.FaultLatched = ExpectedFault);
    IF StepIndex = 12 THEN Done := TRUE; ELSE StepIndex := StepIndex + 1; END_IF;
END_IF;
END_PROGRAM
