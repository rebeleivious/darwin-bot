My code progressions

Note: I am not attaching all the tried codes, just the initial ones and the ones that stood out. Also for each of the attached codes these are the initial codes with those specific variables made using help of gemini
But I tried changing weights on my end to get different results. Initially I kept running func for 20gen filtered good func then ran those for 100 gen then finally the best ones for higher get like 200 and 300.

PreCode1: I tried running with the initial values already given and changing few parameters randomly just to get a gist of what’s going on in the problem , I don’t remember what all changes I tried but I tried initially changing each of the weights by small values keeping everything else more or less fixed. During this initial stage I didn’t have a clarity of what metrics function is doing and how to incorporate it in the fitness function so that remained unedited. I also tried one code on 4 legs with changing some fitness func parameters (weights) and consistently got like 16-17m in 20 gen. It was the starting point of the 4legged supremacy. 

CODE1: I shifted to four legs as cheetah beats Usain Bolt in a race. So 4 legs implies more stability and fast gait. Now we maximized thigh length for longer step length and similarly changed knee length to prevent the knees from knocking together, increased the angle for rotation for longer steps again. Initially we just started changing fitness function by changing weights and adding penalty for backward movement vertical oscillations etc

CODE2: maxed out everything in body. Gave good rewards after they covered good distance(like squaring and cubing), added more constraints to better the walk and penalties.

Code3: One of by first hit codes. Reached like 26m in 100 gen but the walk was not that good

From here on I tried many codes but all of them reached this mark of 20-25m in 100 gen
I tried the cheetah dimensions(42cm,35cm) different weights etc and from here on I started changing config file too,I put few of these codes in trialcodes.py

Code4 and code5: few of my best codes. Reached like 29m, starting point of pushing further.

Finalcode: my most consistent code, always gave 23-27m in 100 gen and reached 29 m in 200 gen







