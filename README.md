# backend

Bu projeyi çalıştırmak için öncelikle requirements.txt içindeki librarylerin "pip install -r requirements.txt --user" komutu ile yüklenmesi gerekiyor. requirements.txt dosyalarında eksik olabilir ya da ilerleyen süreçte yeni requirementslar çıkabilir. Belgeyi güncel tutmakta fayda var.

Projeyi çalıştırmadan önce yapılması gereken ayarlardan biri de .env dosyası oluşturulmasıdır. Güvenlik gerekçelerinden ötürü .env dosyası Proje dosyalarının dışında bırakıldı fakat .env-example dosyası örnek olarak bırakıldı. .env-example içeriği kopyalanıp .env adlı bir dosya oluşturup, içeriğini de çalışmak istenen şekilde doldurmak yeterli olacaktır(Grup üyeleriyle iletişime geçiniz). 

Firebase projesine dahil olduktan sonra(Grup üyeleriyle iletişime geçiniz) project settings kısmındaki service accounts sekmesine girip generate new private key butonuna tıklayıp bir json dosyası indirmeniz gerekiyor. İndirilien dosyanın adını firebase_key.json olarak değiştirip Proje dizinine atmalısınız. 

#Projenin Çalıştırılması
Projeyi çalıştırmak için terminalde "python -m uvicorn main:app --reload" komutu yeterlidir.
