# Corona statistics
Corona statistics. Runs with Python 3+.


## Demo
<img src="demo.gif" width="800">


## How to run
Data from [Johns Hopkins CSSE](https://github.com/CSSEGISandData/COVID-19)

```
$ ./corona.py [-l | -g | -a [c|d|r] | COUNTRY]
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


</br>


**Forecast** based on exponential growth or logistic function (requires `numpy`, `scipy` and `matplotlib`). Set `SHOW=True` if you want to show graph
```
$ ./forecast.py -e | -l [COUNTRY]
```

 - Global forecast
```
$ ./forecast -l | -e
```

 - Country forecast
```
$ ./forecast -l | -e <country>
```
