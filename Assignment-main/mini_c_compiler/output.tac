x = 5
y = 2.5
decl arr[4]
t1 = x + 3
arr[0] = t1
t2 = arr[0]
t3 = t2 * 2
arr[1] = t3
t4 = arr[1]
t5 = t4 > 10
ifFalse t5 goto L1
t6 = arr[1]
t7 = y + t6
y = t7
goto L2
L1:
t8 = y - 1.0
y = t8
L2:
i = 0
L3:
t9 = i < 3
ifFalse t9 goto L4
t10 = arr[i]
t11 = t10 + 1
arr[i] = t11
t12 = i + 1
i = t12
goto L3
L4:
j = 0
L5:
t13 = j < 4
ifFalse t13 goto L6
t14 = arr[j]
print t14
t15 = j + 1
j = t15
goto L5
L6:
print y
