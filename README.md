# Corona statistics
Corona statistics for Sweden. Runs currently only with Python 3+.

## Demo
<img src="demo.gif" width="640">

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
```
$ ./corona.py -a $1
```

 - List all data for specific country
```
$ ./corona.py <country>
```

</br>

Data from [Folkhälsomydigheten](https://www.folkhalsomyndigheten.se/smittskydd-beredskap/utbrott/aktuella-utbrott/covid-19/aktuellt-epidemiologiskt-lage/)
```
$ ./folk.py
```