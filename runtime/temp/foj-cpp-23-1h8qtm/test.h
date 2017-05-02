#include <cstring>
#include <cstdio>

void test() {
    auto f = fopen("t.txt", "w");
    const char* s = "hello world\n";
    fwrite(s, strlen(s), 1, f);
}
