- fish tingz
    + [ ] fish behaviour should be separated to at least 3 groups:
        * TopDweller
        * MidWater  - this is the current model
        * BottomDweller
        this could be different classes all inheriting from base Fish,
        or just an Enum based distinctions

    + [ ] fish should somehow not try drawing over eachother
        * the Aquarium could keep track of printed positions per frame
        * this is a bit problematic, because it needs to loop through Fish().skin and get if its been printed to.
 
    + [ ] do something a bit nicer with the half-baked Boundary class integration into Fish

- aquarium class
    + [ ] dumping and loading from files

- ui
    + [ ] <em>FIRST</em> pytermgui needs to be rewritten to support typing, and allow better code quality.
    + [ ] <em>THEN</em> make ui for saving and loading Aquariums
