- fish things
    + [x] fish behaviour should be separated to at least 3 groups:
        * TopDweller
        * MidWater  - this is the current model
        * BottomDweller
        * this could be different classes all inheriting from base Fish, or just an Enum based distinctions

    + [ ] rewrite Fish().update() method
        * [x] fish should stop 1 char before the food, and set their heading towards the food
        * [ ] implement different behaviours by Fish().type
        * [ ] there should be a cooldown for eating

    + [ ] reimplement fish naming stuff

    + [ ] fish should somehow not try drawing over eachother
        * the Aquarium could keep track of printed positions per frame
            - this can be done using the fish.show() method, which could return an array of Positions
 
    + [ ] do something a bit nicer with the half-baked Boundary class integration into Fish

    + [ ] Fish properties could be FishPropeties subclasses, and users could create their own using json
        * something like: 
            ```python
            class Corydoras(FishProperties):
                type: BOTTOM_DWELLER
                stages: [..,...,...,]
                pigment: [242, 238, 238, 242]
                variants: FishVariants.PANDA
            ```  

    + [ ] implement a breeding system!

- aquarium class
    + [ ] dumping and loading from files

- ui
    + [ ] rewrite NewfishDialog class to support the new Fish().\_\_init\_\_ method
    + [ ] <em>FIRST</em> pytermgui needs to be rewritten to support typing, and allow better code quality.
    + [ ] <em>THEN</em> make ui for saving and loading Aquariums
