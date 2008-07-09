def leven(s, t):
    m, n = len(s), len(t)
    d = [range(n+1)]
    d += [[i] for i in range(1,m+1)]
    for i in range(0,m):
        for j in range(0,n):
            cost = 1
            if s[i] == t[j]: cost = 0
            d[i+1].append( min(d[i][j+1]+1, # deletion
                              d[i+1][j]+1, #insertion
                              d[i][j]+cost) #substitution
                         )
    return d[m][n]

