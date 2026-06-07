from pyswip import Prolog

prolog = Prolog()

for result in prolog.query("member(X,[1,2,3])"):
    print(result)