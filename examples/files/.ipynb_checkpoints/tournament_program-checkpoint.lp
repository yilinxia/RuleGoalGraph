person(A) :- parent(A,_).
person(B) :- parent(_,B).
has_father_mother(A) :- person(A) , father(_,A), mother(_,A).
icv_person_has_father_mother(A) :- person(A), not has_father_mother(A).  