import sys

s1 = int(sys.argv[1])

dict = {}

def control(id) :
    if id in dict :
        return true
    else : 
        return false

while s1 > 0 :
    text = input("Lütfen birer boşluk bırakarak sırayla numara, ad, soyad ve yaş bilginizi giriniz:").split()
    
    s2 = len(text)
    if control(text[0]) == true :

        if s2 == 4 :
            no = int(text[0])
            ad = text[1]
            soyad = text[2]
            yas = int(text[3])
        elif s2 > 4 :
            no = int(text[0])
            ad = text[1:-2]
            soyad = text[-2]
            yas = int(text[-1])        

        t1 = (ad,soyad,yas) 
        dict[no] = t1
        s1 -= 1

    else :
        print("Girdiginiz numara sözlükte bulunmakta!")   


dict={key:dict[key] for key in sorted(dict.keys())}
print(dict)