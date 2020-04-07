# Corona statistics
Corona statistics. Runs with Python 3+.


## Demo
<img src="demo.gif" width="800">


## How to run
Data from [Johns Hopkins CSSE](https://github.com/CSSEGISandData/COVID-19)

```
$ ./corona.py -l | -g | -a [c|d|r|cn|dn|rn|p] | COUNTRY
```

 - List countries
```
$ ./corona.py -l
```

 - List global data
```
$ ./corona.py -g
```

 - List latest data for all countries and sort by $1:
   - `c`: Confirmed
   - `d`: Deaths
   - `r`: Recovered
   - `cn`: New cases confirmed
   - `dn`: New cases dead
   - `rn`: New cases recovered
   - `p`: Percentage of cases that are fatal
```
$ ./corona.py -a $1
```

 - List all data for specific country
```
$ ./corona.py <country>
```


### Forecast 
 - Plots graph and outputs data based on exponential and logistic functions
   - **Requires** `numpy`, `scipy` and `matplotlib`
```
$ ./forecast.py [COUNTRY]
```

</br>

<img src="figure.png" width="800">
