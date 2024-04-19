#include <stdio.h>

int print_age();

int main() {
	printf("Hello world\n");
}

int print_age() {
	int x = 0;
	int y = 5;
	x += y;
	printf("You are %d years old\n", x);
}
