import sys

s1 = int(sys.argv[1])
dict = {}

while s1 > 0 :

    text = input("Lütfen birer boşluk bırakarak sırayla numara, ad, soyad ve yaş bilginizi giriniz:").split()

    try:
        test = int(text[0])
    except ValueError:
        print("Numara olarak bir sayı giriniz!")
    else:
        try:
            test2 = int(text[-1])
        except ValueError:
            print("Yas olarak bir sayı giriniz!")
        else: 
            no = int(text[0])
            ad = text[1:-2]
            soyad = text[-2]
            yas = int(text[-1])

            if no in dict :    
                print("Girdiginiz numara sözlükte bulunmakta!")        

            else:
                t1 = (ad,soyad,yas)
                dict[no] = t1
                s1 -= 1  

dict={key:dict[key] for key in sorted(dict.keys())}
print(dict)
