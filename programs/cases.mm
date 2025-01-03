import predicate_calculus/axioms/constructive_dilema

Show (a & b) <-> (b & a)
From {}

    Show (a & b) <-> (b & a)
    From {a}

        Show (a & b) <-> (b & a)
        From {b}
            (a & b) <-> (b & a)
        Conclude

        Show (a & b) <-> (b & a)
        From {~b}
            (a & b) <-> (b & a)
        Conclude
        
        Thus b -> ( (a & b) <-> (b & a) )
        Thus ~b -> ( (a & b) <-> (b & a) )
        Thus (a & b) <-> (b & a)

    Conclude

    Show (a & b) <-> (b & a)
    From {~a}

        Show (a & b) <-> (b & a)
        From {b}
            (a & b) <-> (b & a)
        Conclude

        Show (a & b) <-> (b & a)
        From {~b}
            (a & b) <-> (b & a)
        Conclude
        
        Thus b -> ( (a & b) <-> (b & a) )
        Thus ~b -> ( (a & b) <-> (b & a) )
        Thus (a & b) <-> (b & a) 

    Conclude

    Thus a -> ( (a & b) <-> (b & a) )
    Thus ~a -> ( (a & b) <-> (b & a) )
    Thus (a & b) <-> (b & a) 

Conclude 
