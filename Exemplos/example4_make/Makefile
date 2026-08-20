SRC = $(wildcard *.cpp)
OBJECTS = $(addsuffix .o, $(basename $(SRC)))

OBJ = $(basename $(wildcard *.cxx))

all:
	$(MAKE) compile
	$(MAKE) hello
	$(MAKE) run

.cpp.o:
	$(CXX) -c $<

test:
	@echo $(SRC)
	@echo $(OBJECTS)

compile: $(OBJECTS)


hello: $(OBJECTS)
	$(CXX) $(OBJECTS) -o hello

run:
	@./hello

GARBAGE = $(wildcard *.o *~)
clean:
	rm $(GARBAGE)

cleanAll:
	rm -f hello
	$(MAKE) clean

test2:
	echo $(OBJ)
