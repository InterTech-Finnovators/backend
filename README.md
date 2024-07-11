# backend

Bu projeyi çalıştırmak için öncelikle requirements.txt içindeki librarylerin "pip install -r requirements.txt" komutu ile yüklenmesi gerekiyor. requirements.txt dosyalarında eksik olabilir ya da ilerleyen süreçte yeni requirementslar çıkabilir. Belgeyi güncel tutmakta fayda var.

Projeyi çalıştırmadan önce yapılması gereken ayarlardan biri de .env dosyası oluşturulmasıdır. Güvenlik gerekçelerinden ötürü .env dosyası Proje dosyalarının dışında bırakıldı fakat .env-example dosyası örnek olarak bırakıldı. .env-example içeriği kopyalanıp .env adlı bir dosya oluşturup, içeriğini de çalışmak istenen şekilde doldurmak yeterli olacaktır. 

#Projenin Çalıştırılması

Projeyi çalıştırmak içöin terminalde "fastapi dev run" komutu yeterlidir. Diğer bir yöntem ise "uvicorn app:app --reload" komutudur
