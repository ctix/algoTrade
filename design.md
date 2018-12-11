
# DESIGN MEMO ES

### Patterns and features recognition Machine Learning   
1. ** scikit-learn  ** 
1. ** Auto-Learn **
    The two Kits with enough packages to train the historical datum from TDX
    
### The Principle:
** Simplify ** 
** Test Driven Development ** 
    1. Write and simply maintain the test file ahead of the real coding 
    2. Run pytest first, ready to fail ,and then coding rectify the test and pass 
    3. Loop , write and annotation the next goals ,in details
** Clearly Marked the Key purpose in a Structured Way   

### PSEUDO WORKFLOW
1. Starting from a given date , specified fund amount , with position management
2. Scan every stock in the interest list , calculation total gain /lose money .
3. make it testable. Utilizing a Test Driven Development methodology  
    * Employing User case and scenarios 
4. Finding a upwards trend stock, starting the simulation of the transaction/trading ,
    * which supposed to begin with daily regression/downwards ,establish preferable
  buy in position in minute line ,May it be starting HIGH FREQUENCY TRANSACTION
5. With the help of the signals and positions, and strategies Learned either from Neural Networking
    or Reinforcement Learning , fund management and position management
 till the end of the data set
 coding functions to pandas day and week data set
 basic dataset include ohlc ,cci ,mas ,booing line
 how to compute the probabilities of close price ,Bayesian Methods???
 write to mysql database of the whole years of day ,minutes basic features


