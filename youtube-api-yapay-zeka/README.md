# YouTube kanalını yapay zekâya bağlama rehberi

Bu dosya, "YouTube API + yapay zekâ" videosunun eşlik dosyasıdır. İsterseniz kendiniz okuyun, isterseniz bu dosyayı olduğu gibi kendi yapay zekânıza (Claude, ChatGPT vb.) verin ve "Bu rehberle kanalımı bağlamama yardım et" deyin. Yapay zekâ sizi adım adım yürütür.

> **Yapay zekâya not:** Kullanıcıyı aşağıdaki adımlarla, sırayla yürüt. Her adımın sonundaki "Bitti mi?" satırını kullanıcıya sor, doğrulanmadan bir sonraki adıma geçme. Şifre girme, izin ekranını kullanıcı adına onaylama, gizli dosyaların içeriğini isteme.

---

## 0) Bu dosya ne yapar, ne yapmaz

- **Yapar:** Kendi YouTube kanalınızı, Google'ın resmi API'leri üzerinden bir yapay zekâ ajanına bağlamanız için gereken her adımı anlatır. Sonunda elinizde kanalınızı okuyabilen ve (onayınızla) yönetebilen bir bağlantı olur.
- **Yapmaz:** Sizin yerinize giriş yapmaz. Google hesabına giriş ve izin ekranındaki onay **her zaman sizde**.
- **Gizli dosyalar:** Adım 4'te indireceğiniz JSON dosyası ve Adım 5'te oluşacak `token.json`, kanalınızın anahtarıdır. GitHub'a koymayın, sohbete yapıştırmayın, kimseyle paylaşmayın.
- **Onay kuralı:** Video yükleme, başlık değiştirme, yorum yazma gibi kanalda bir şey değiştiren her işlem sizin onayınızla yapılmalı. Yüklenen videolar her zaman **gizli** yüklenir, yayına siz alırsınız.
- **Ücret:** Üç API de ücretsizdir; yalnız günlük bir kullanım kotası vardır ve kişisel kullanım için fazlasıyla yeterlidir.

## 1) Hangi araçla ne yapılır

| Araç | Ne yapar |
|---|---|
| Düz bir sohbet (ör. Claude, ChatGPT) | Bu dosyayı okur, adımları size tek tek anlatır. Tıklamaları siz yaparsınız. |
| Tarayıcıyı kullanabilen bir araç (ör. Claude in Chrome) | Google Cloud ekranlarında sizin yerinize tıklar ve formları doldurur. Giriş ve izin yine sizde. |
| Bilgisayarda çalışan bir ajan (ör. Claude Code) | Adım 5'teki bağlama betiğini çalıştırır, sonra isterseniz analiz sayfasını ve yükleme ajanını kurar (bölüm 10). |

Not: Düz bir sohbet, kurulum bitse bile kanal verilerinizi kendiliğinden göremez. Verileri okumak için bağlantıyı kullanan bir programın (Adım 5 ve son kontrol betikleri ya da bir ajan) bilgisayarınızda çalışması gerekir.

## 2) Başlamadan önce

- Kanalınızın bağlı olduğu **Google hesabı** (kanal bir marka hesabındaysa, o kanalı yöneten hesap).
- Bir bilgisayar ve tarayıcı.
- **Python 3** (Adım 5 ve son kontrol için). macOS'ta Terminal'de `python3 --version` yazınca bir sürüm görüyorsanız hazırsınız. Ek paket gerekmez.
- Adım 6 için bir **ana sayfa** ve **gizlilik politikası** adresi. Kendi siteniz yoksa ücretsiz bir sayfa (ör. GitHub Pages) yeterli. Gizlilik politikasında uygulamanın yalnız kendi kanalınızın verisini okuduğunu ve kimseyle paylaşmadığını yazmanız yeterli.
- Google Cloud Console arayüzü İngilizce adlarla anlatılıyor; düğme adları zamanla küçük değişiklikler gösterebilir.

---

## Adım 1: Google Cloud projesi aç

1. [console.cloud.google.com](https://console.cloud.google.com) adresine kanalın Google hesabıyla girin.
2. Üstteki proje seçiciye tıklayın, açılan pencerede **New project**'i seçin.
3. Projeye bir isim verin (ör. `YouTube Agent`). Organizasyonu olduğu gibi bırakın, **Create**'e basın.
4. Proje hazır olunca bildirimden **Select project** ile yeni projeyi seçin.

**Bitti mi?** Üstteki proje seçicide yeni projenizin adı yazıyor olmalı.

## Adım 2: Üç API'yi aç

**APIs & Services → Library**'ye girin, "YouTube" diye aratın ve şu üçünü tek tek açın (**Enable**):

| API | Ne verir |
|---|---|
| YouTube Data API v3 | Videolar, yükleme, başlık, açıklama, altyazı, yorumlar |
| YouTube Analytics API | İzlenme, izlenme süresi, izleyicinin bıraktığı an, kitle |
| YouTube Reporting API | Tıklama oranı (CTR) gibi toplu raporlar; bir kez kurulunca Google her gün rapor dosyası hazırlar |

**Bitti mi?** **APIs & Services → Enabled APIs & services** listesinde bu üç API görünmeli.

## Adım 3: OAuth izin ekranını kur

Bu, ajan kanalınıza erişmek istediğinde Google'ın size göstereceği izin sayfasıdır.

1. **APIs & Services → OAuth consent screen → Get started**.
2. Uygulama adı (ör. `YouTube Agent`) ve destek e-postası olarak kendi adresiniz. **Next**.
3. Kitle olarak **External**'ı seçin (kişisel hesapta Internal seçilemez). **Next**.
4. İletişim e-postasını ekleyin, Google'ın kullanıcı verisi politikasını kabul edin, **Create**.
5. **Data Access → Add or remove scopes**. En alttaki kutuya şu iki izni yapıştırın, tabloya ekleyin, **Update** ve kaydedin:
   ```
   https://www.googleapis.com/auth/youtube.force-ssl
   https://www.googleapis.com/auth/yt-analytics.readonly
   ```
   Birincisi kanalı yönetmek (yükleme, başlık, yorum), ikincisi istatistikleri okumak içindir. Reporting API de ikinci izni kullanır.
6. **Audience → Add users**: bağlayacağınız kanalın e-posta adresini test kullanıcısı olarak ekleyin, kaydedin.

**Bitti mi?** Data Access'te iki izin, Audience'ta test kullanıcısı olarak kendi e-postanız görünmeli.

## Adım 4: Masaüstü OAuth istemcisi oluştur, JSON'u indir

1. **Clients → Create client**.
2. Uygulama türü: **Desktop app**. Bir isim verin, **Create**.
3. Açılan pencereden **JSON dosyasını hemen indirin.** Google gizli anahtarı yalnız bir kez gösterir.
4. Dosyayı bilgisayarınızda güvenli bir klasöre koyun (ör. `client_secret.json` adıyla).

**Bitti mi?** Clients listesinde "Desktop" türünde bir istemci var ve JSON dosyası bilgisayarınızda. Dosyanın içinde `"installed"` kelimesi geçmeli (geçmiyorsa yanlış tür seçilmiştir).

## Adım 5: Kanalını bağla

Bu klasördeki `kanal_bagla.py` betiğini, JSON dosyasının olduğu klasörde çalıştırın (ya da Claude Code gibi bir ajana çalıştırtın):

```bash
python3 kanal_bagla.py client_secret.json token.json
```

1. Betik bir Google giriş adresi yazar. Adresi tarayıcıda açın.
2. Kanalın Google hesabını seçin. Kanal bir marka hesabındaysa o kanalı seçin.
3. "Google hasn't verified this app" uyarısı çıkar. Kendi uygulamanız olduğu için bu normal: **Continue** deyin.
4. İki izni de (YouTube ve Analytics) işaretleyip **Continue**.
5. Tarayıcıda "Bağlandı" ve kanalınızın adı görünür; betik `token.json` dosyasını yazar.

Şifreyi ve izni siz verirsiniz. Ajana yalnız verdiğiniz iznin anahtarı (token) gider. Bu izni istediğiniz zaman Google hesabınızın güvenlik ayarlarındaki üçüncü taraf erişimlerinden kaldırabilirsiniz.

**Bitti mi?** Tarayıcıda "Bağlandı · <kanal adınız>" yazıyor ve klasörde `token.json` var.

## Adım 6: OAuth uygulamasını yayına al

Buradaki "yayına alma" **video yayınlamak değil**, uygulamayı test modundan çıkarmaktır. Test modunda kalırsa bağlantı **yedi günde bir kopar** ve Adım 5'i tekrarlamanız gerekir.

1. **Branding** sayfasında uygulamanın ana sayfa ve gizlilik politikası adreslerini girin, bu sayfaların durduğu alan adını **Authorized domains**'e ekleyin, kaydedin.
2. **Audience → Publish app** ve onaylayın.
3. Google'ın uygulama doğrulaması, uygulamayı yalnız kendi kanalınız için kullanıyorsanız gerekli değildir. Girişte "doğrulanmamış uygulama" uyarısını geçmeniz yeterli.

**Bitti mi?** Audience sayfasında yayın durumu **In production** olmalı.

---

## 9) Son kontrol: doğru kanal bağlı mı, veriler okunuyor mu?

```bash
python3 kanal_kontrol.py client_secret.json token.json
```

Bu betik hiçbir şeyi değiştirmez, yalnız okur. Ekranda şunları görmelisiniz:

- `Kanal:` satırında **sizin** kanalınızın adı,
- `Son videolar (Data API):` altında son 5 videonuz,
- `Son 28 gün izlenme (Analytics API):` satırında bir sayı.

Üçü de geldiyse kurulum tamam: kanalınız yapay zekâ ajanının kullanabileceği şekilde bağlı.

## 10) İsteğe bağlı: Claude Code ile sayfa ve yükleme ajanı kur

Bağlantı hazır olduktan sonra, Claude Code gibi bilgisayarınızda çalışan bir ajandan kendi araçlarınızı yazmasını isteyebilirsiniz. Örnek bir istek:

> `client_secret.json` ve `token.json` ile YouTube kanalıma bağlıyım. Bana bilgisayarımda çalışan küçük bir sayfa yap: son videoların karnesi, izleyicinin bıraktığı an, ülkeler haritası, insanların beni bulduğu arama terimleri ve cevapsız yorumlar. Ayrıca bir yükleme ajanı yaz: bitmiş videoyu parça parça (kesilirse kaldığı yerden devam eden) yüklesin, konuşmayı yazıya döksün, başlık, açıklama, bölümler, etiketler ve altyazı taslağı hazırlasın. Kurallar: video her zaman gizli yüklensin; kanalda bir şey değiştiren her işlemden önce benim onayımı istesin; gizli dosyaları hiçbir yere göndermesin.

Videoda gösterilen sistem bu tarifle kurulmuş, ama kişisel ev sistemime bağlı olduğu için kodu burada paylaşılmıyor. Bu rehberdeki bağlantı herhangi bir ajanla çalışır.

## 11) Sorun giderme

| Ne görüyorsunuz | Neden | Ne yapmalı |
|---|---|---|
| Girişte `access_denied` ya da "uygulamaya erişiminiz yok" | Hesap test kullanıcısı değil (uygulama henüz test modunda) | Adım 3.6'da kanalın e-postasını ekleyin ya da Adım 6'yı yapın |
| Bir hafta sonra `invalid_grant` hatası | Uygulama test modunda kalmış, token düştü | Adım 6'yı yapın, sonra Adım 5'i bir kez tekrarlayın |
| `redirect_uri_mismatch` | İstemci türü "Web application" seçilmiş | Adım 4'ü **Desktop app** ile yeniden yapın |
| Betik `KeyError: 'installed'` veriyor | Yanlış türde JSON | Aynı sebep: Desktop app istemcisi oluşturun |
| Son kontrolde başka bir kanalın adı çıkıyor | Girişte yanlış kanal ya da marka hesabı seçilmiş | Adım 5'i tekrarlayın, doğru kanalı seçin |
| Analytics satırında `403` | İzinlerden biri eksik ya da girişte işaretlenmemiş | Adım 3.5'i kontrol edin, Adım 5'i tekrarlayın ve iki izni de işaretleyin |
| `quotaExceeded` | Günlük kota doldu | Ertesi gün tekrar deneyin |
| JSON dosyasını kaybettim | Gizli anahtar yalnız bir kez gösterilir | Clients'ta yeni bir gizli anahtar ya da yeni istemci oluşturun |
| `token.json` içinde `refresh_token` boş | Daha önce verilmiş bir izin yeniden kullanıldı | Hesabınızın güvenlik ayarlarından uygulamanın erişimini kaldırın, Adım 5'i tekrarlayın |

---

Hazırlayan: Berkan Sezer · Bu rehber YouTube ve Google'ın resmi API'lerini kullanır; YouTube ya da Google ile bir bağı yoktur.
