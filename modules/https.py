#!/usr/bin/python3
#=========================#
#  Kitsune by @JoelGMSec  #
#    https://darkbyte.net #
#=========================#

import os
import sys
import ssl
import http.server

cert_file = '/tmp/Kitsune/http/server.crt'
key_file = '/tmp/Kitsune/http/server.key'

cert_pem = b"""
-----BEGIN CERTIFICATE-----
MIIDBzCCAe+gAwIBAgIUMAvX07574dsmtAhEsg9mkQipRnAwDQYJKoZIhvcNAQEL
BQAwEjEQMA4GA1UEAwwHS2l0c3VuZTAgFw0yNDA3MDkwODMwNDFaGA80NzYyMDYw
NTA4MzA0MVowEjEQMA4GA1UEAwwHS2l0c3VuZTCCASIwDQYJKoZIhvcNAQEBBQAD
ggEPADCCAQoCggEBAKcHxmfjlqLMQ3Xc/0KqaD8Kh2w9ULQWmbVv5v1ZTrVjjMCs
TNdj/UIgbQreVdu7tBL8DC2Rwhxat7Jpfs12tvzIHUfsZ46vyNP0tX5k7prPoeKt
vGHK3/kTrVKBQrQZgcJlHqEQWj4+2noeKHFX0e2U7LMDqaRdkrCMwJExs635V1FO
smrOJ8BEn8FpN8Byy1ffzolbsnny3mR7BcuEJ/5x36DjdYFxI37LOVnbMMZ2+3kU
O1Qui834CxIUbA4Ax+QerY1pZAWpQmb4CIGVo4lTUrR02ZtmMJq9KSpNhfdAaE3G
RDrB3WikMzP2EGqoNLDoUP8YEFRbYlARO7ZL6ZsCAwEAAaNTMFEwHQYDVR0OBBYE
FD9SbW/PW7X8AHC+W9cANAg530OVMB8GA1UdIwQYMBaAFD9SbW/PW7X8AHC+W9cA
NAg530OVMA8GA1UdEwEB/wQFMAMBAf8wDQYJKoZIhvcNAQELBQADggEBADzqvfCI
4YBGbRLEsBnMooT9GBU3JossNBiBw8hdHamVQgy0C/tTIMMwbUoqO0IUh+0beIvl
yXHTfZ+3yoa/FfDX7Zx0QO1UcuZtiXf5sgem2tBYBeSoCrrz2JbkQz/OoJp75Su/
uumiF+wYmZfjvpW5rjhWlU/bsq354OTyqJx74e179+ccF6G4rf2L1SsiNGcMFdAI
mzEMnzyYsVkzcxjWr0dC4UeG6FbISvQBNGyETfNsW1pxKD/K7U10VwEJtRsEnAs/
vnIPOfawBoJ/90lwka6SUJa8k2k7/n1HIDt1ksNUucN+9PquYUlqNoGEzcsKxU4i
yk3BveBp0cj5Xz0=
-----END CERTIFICATE-----
"""

key_pem = b"""
-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCnB8Zn45aizEN1
3P9Cqmg/CodsPVC0Fpm1b+b9WU61Y4zArEzXY/1CIG0K3lXbu7QS/AwtkcIcWrey
aX7Ndrb8yB1H7GeOr8jT9LV+ZO6az6Hirbxhyt/5E61SgUK0GYHCZR6hEFo+Ptp6
HihxV9HtlOyzA6mkXZKwjMCRMbOt+VdRTrJqzifARJ/BaTfAcstX386JW7J58t5k
ewXLhCf+cd+g43WBcSN+yzlZ2zDGdvt5FDtULovN+AsSFGwOAMfkHq2NaWQFqUJm
+AiBlaOJU1K0dNmbZjCavSkqTYX3QGhNxkQ6wd1opDMz9hBqqDSw6FD/GBBUW2JQ
ETu2S+mbAgMBAAECggEAGSYTCfZa6mUd7SOarWNx8bf4nuP2gD784rQYD+I/9xCn
kyT+JtoPukKemGnUfJKc8NTRUpUlKFbCXNMEfBQZRiMtQXSHPRUbhEpOf1rcECQe
CD7HY+QDaAG98XOz4uEKSAYon/CR3dhh1cwvo60o1wA6yVNOWgiauwlePx5AIvvu
um4aGX2C228MdJx92zQfsY6obzmGbkG6dZwEZ5884jVfirP8/LcBkQ6Y89j8XTF2
VJsPt5tm4RVnRvuJjxHkOMYpjYsggECbmvybBBCdbkUYPeY2jjfFK/WX5x7WOZws
TGC6mIuPVe36OkfKdFfKV8LNVlZokWmgIKU4Gdw+BQKBgQDl7kuRZPe5rvma4gj6
GEnTQ9EBDFdeECtCe7Pf7Pbupg74ivx+ZygKWGrkm1jc2+XoNLKqwNO/zB8Hgu0n
dhR5vJ66u3FaJUoivenGcEV189X2/x0u0rTwlYW++yZrmpnAd5BtZstAcmgGQaZB
m6j/P9FLhGtiR04j/U7ismJxZQKBgQC5983W+hhetdSt8aD1WLiEvZ35ODcSWmQV
SpYjykyB1WBueJdqsJdCbL6VnjKfgwD1A9KofcrV2m6LWg0kOdA6ATJk5wslHtqy
jSx038HZyeHnJ/0z0haqxeGBb+2W9UsxeuM40sq01+YQbXqv0Lc/uiTO1oj1MYK6
jER5poS+/wKBgG+wuJ6Q+FEHcRJOeGPcRohMagtjTlFP82OhKXg96Jl2qtEK2qog
O/ACkTIpUBpA60ZHyv5tGq8RXYVNkRvZHQshl81HXkGW2ZNUw2l0ghlQ7//CXw+u
pNw1Fbn2z+v3Nnaq3cp244aTzHo1i6hVD9ulyWowkeU0k/2hf59ZXb6NAoGAGaEV
NTNyeFsG3JIYZLe9dk3Ln7UnodfjQyvsVTJkKOCHUbI86+86aWUjPut2fpVHZH0K
Yz4y3hYkdgALH5r4H4Zas51D4/HEoibioZjU1ncEMx9HvgSOKyrqUTRjwhI8Mq2E
8yfZ1+KJSmpMJj7Vgmrc98SJS4FvStZZ+YoBcXECgYBID1TfRvR/cPEY8Kk+d6DV
s+AGw5vDQ/iahZaqauqpujVTgFyt4qiZLl/wr7eZOquiOlxLOYgxXMjU/LcEpFFH
EJOoU91jxrXZoX6JphuDjimqhy4t3NtFHzHdq0pRCFnwXGFpRkYGC8BBooe5rrdx
W8InjQlg7E/428zPRtKp8A==
-----END PRIVATE KEY-----

"""

os.makedirs('/tmp/Kitsune/http/', exist_ok=True)
with open(cert_file, 'wb') as f:
    f.write(cert_pem)

with open(key_file, 'wb') as f:
    f.write(key_pem)

ip = sys.argv[1]
path = sys.argv[2]
port = sys.argv[3]

ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ctx.load_cert_chain(certfile=cert_file, keyfile=key_file)
server_address = (ip, int(port)) ; os.chdir(path)  
httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)

try:
    httpd.serve_forever()

except:
    pass