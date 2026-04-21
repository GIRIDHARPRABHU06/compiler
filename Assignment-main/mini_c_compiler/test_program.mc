int x = 5;
float y = 2.5;
int arr[4];

arr[0] = x + 3;
arr[1] = arr[0] * 2;

if (arr[1] > 10) {
    y = y + arr[1];
} else {
    y = y - 1.0;
}

int i = 0;
while (i < 3) {
    arr[i] = arr[i] + 1;
    i = i + 1;
}

for (int j = 0; j < 4; j = j + 1) {
    print(arr[j]);
}

print(y);
