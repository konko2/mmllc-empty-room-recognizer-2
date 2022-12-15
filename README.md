# Tasks
1. optimize parameters
   * there are 8 parameters right now, only two of them are float
   * I need labeled thumbnails. How can I get them: 
   I can run model with init parameters and then manually select and correct labels for edge cases 
   and also take some stable thumbnails
   * How much data do I need? 
   lets say each parameter could have one extremum => we can try approx with square func
   for one square function there's 3 points needed to build unique poly
   => lets say 3*8 = 24. Ok, over 100 would be def. enough
   * How can I quickly label data?
     1. upload lots of different cases, would be nice if they would be different as much as possible.
     only top of any? I guess top rooms would have more movement
     2. build a chart for the final limiting values
     3. get some amount of closest to init limit thumbnails in one folder by pairs, name it conseq
     4. move pairs of images into specific folder for category
   
   * how to learn integer parameters?
   * what are the limits?
   * how to estimate the success rate?
2. find out models bottlenecks
   * running text lines? chat?
3. find out the success rate
4. build http server
5. build preview on live data?
6. get daily data for Evgenii