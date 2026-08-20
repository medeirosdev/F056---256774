# search for pattern hello and replace it with world
sed 's/world/WORLD/' input.txt

# search for pattern CFLAGS, in the same line search for pattern -Wall and replace it with -Wall -fPIE
sed '/CFLAGS/ s/-Wall/-Wall -fPIE/' configure
