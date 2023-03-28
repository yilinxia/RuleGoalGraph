dom(1..5).
e(X,Y) :- dom(X), dom(Y), X!=Y.
e(Y,X) :- e(Y,X).

d(X,Y) :- d(X,Z), d(Z,Y).
d(X,Y) ; d(Y,X) :- e(X,Y).

not_start(X) :- d(_,X).
start(X) :- dom(X), not not_start(X).
not_end(X) :- d(X,_).
end(X) :- dom(X), not not_end(X).
