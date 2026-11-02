within ;
package TankPump "Illustrative offline tank/pump digital-twin models"
  block Controller "Sampled hysteresis with a latched observation-integrity fault"
    parameter Real Ts(unit="s") = 0.1;
    parameter Real low(unit="m") = 0.30;
    parameter Real high(unit="m") = 0.70;
    parameter Real trip(unit="m") = 0.95;
    input Real measuredLevel(unit="m");
    input Boolean enabled;
    input Boolean fresh;
    input Boolean reset;
    output Boolean pumpOn(start=false, fixed=true);
    output Boolean faultLatched(start=false, fixed=true);
  initial equation
    assert(Ts > 0 and 0 <= low and low < high and high < trip,
      "Require Ts>0 and 0<=low<high<trip");
  algorithm
    when sample(0, Ts) then
      if not fresh or measuredLevel >= trip then
        faultLatched := true;
        pumpOn := false;
      elseif pre(faultLatched) and not reset then
        faultLatched := true;
        pumpOn := false;
      else
        faultLatched := false;
        if not enabled then
          pumpOn := false;
        elseif measuredLevel <= low then
          pumpOn := true;
        elseif measuredLevel >= high then
          pumpOn := false;
        else
          pumpOn := pre(pumpOn);
        end if;
      end if;
    end when;
  end Controller;

  model Demonstrator "Uncalibrated physical reference model; no equipment connection"
    parameter Real area(unit="m2") = 1.0;
    parameter Real inflow(unit="m3/s") = 0.05;
    parameter Real outflow(unit="m3/s") = 0.02;
    parameter Real biasMagnitude(unit="m") = 0.0;
    Real level(unit="m", start=0.50, fixed=true);
    Real measuredLevel(unit="m");
    Controller controller;
  equation
    assert(area > 0 and inflow > outflow and outflow >= 0,
      "Invalid illustrative physical parameters");
    der(level) = ((if controller.pumpOn then inflow else 0.0) - outflow)/area;
    measuredLevel = level + (if time >= 15 and time < 18 then biasMagnitude else 0.0);
    controller.measuredLevel = measuredLevel;
    controller.enabled = true;
    controller.fresh = not (time >= 20 and time < 25);
    controller.reset = time >= 26 and time < 26.2;
    annotation(experiment(StartTime=0, StopTime=60, Interval=0.1, Tolerance=1e-8));
  end Demonstrator;

  model BiasedSensor "Compare with Demonstrator under a declared measurement bias"
    extends Demonstrator(biasMagnitude=0.25);
  end BiasedSensor;

  model ControllerChecks "Twelve shared decision cases; assertions follow sampling"
    Controller c(Ts=1.0);
    parameter Real levels[12] = {0.50,0.30,0.50,0.70,0.20,0.20,0.20,0.20,0.20,0.95,0.95,0.50};
    parameter Boolean enables[12] = {true,true,true,true,false,true,true,true,true,true,true,true};
    parameter Boolean freshness[12] = {true,true,true,true,true,true,false,true,true,true,true,true};
    parameter Boolean resets[12] = {false,false,false,false,false,false,false,false,true,false,true,true};
    parameter Boolean expectedPump[12] = {false,true,true,false,false,true,false,false,true,false,false,false};
    parameter Boolean expectedFault[12] = {false,false,false,false,false,false,true,true,false,true,true,false};
    Integer k;
  equation
    k = min(12, integer(floor(time)) + 1);
    c.measuredLevel = levels[k];
    c.enabled = enables[k];
    c.fresh = freshness[k];
    c.reset = resets[k];
  algorithm
    when sample(0.001, 1.0) then
      assert(c.pumpOn == expectedPump[k], "Pump command differs from shared policy case");
      assert(c.faultLatched == expectedFault[k], "Fault latch differs from shared policy case");
    end when;
    annotation(experiment(StartTime=0, StopTime=11.1, Interval=0.1));
  end ControllerChecks;
end TankPump;
