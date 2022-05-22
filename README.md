# Autocolumner
Code and drawings for an open source autocolumner

## Future Ideas
- use Nanpy Stepper function where possible (done) or AccelStepper library. Latter is preferred but need to port AccelStepper over to Nanpy first which is non trivial (link: http://www.airspayce.com/mikem/arduino/AccelStepper/). Benefits include: non-blocking API functions and not having to use for loops to implement stepper motion for A4988 drivers (the ULN2003 is wrapped nicely with the Nanpy Stepper library but no such function for A4988 exists just yet)
-  write unit tests for each of the modules and implement with git hooks (pre-commit). Given that there's no way for the script to monitor whether hardware does what it's supposed to do here's a proposed workaround. For each hardware component / method, test that particular component and prompt for user input (pass/fail). If pass, go to the next component. If fail, prompt whether to terminate the script or continue with tests? Print out a summary of results at the end. It might be useful to have a separate set of tests just for the software modules.

## Attributions
- 02/04/2022 peristaltic pump design based on Ralf's from thingiverse (link: https://www.thingiverse.com/thing:254956) and Great Scott's design (link: https://www.youtube.com/watch?v=AMiXme4bMUk).
- 16/05/2022 MG996R Freecad model is Jozef Kutej's design, (link: https://blog.kutej.net/2020/12/1st-freecad)
- 18/05/2022 Helper script added for extracting coordinates of fraction tubes from photo. Written by Pantelis Liolios (link: https://github.com/pliolios/curvedigitizer)
