# Crane Bell Korea

cranebell.rubiworkshop.com 원페이지 정적 사이트. quoc.rubiworkshop.com과 같은 레이아웃 · 서체 · 빌드 방식이며, 제품 사진 처리는 white(화이트 인더스트리) · paul 사이트와 같습니다.

- `index.html` 한국어 원페이지 (Crane · Range · E-ne · Mini Suzu · Mini Karen · Riten · Finish · Build Match · Showroom)
- 범위: 루비워크샵(rubiworkshop.com/brand-cranebell)과 루비서플라이(rubisupply.com/cranebell)에서 취급하는 모델만. 이네 벨 · 미니 스즈 벨 · 미니 카렌 벨은 두 채널 모두, 리튼 벨은 루비서플라이 거래처 공급.
- 디자인은 rubi.kr 체계: 영문 Pretendard · 한글 에스코어 드림, 웨이트 400, 흑백과 얇은 라인, 각진 버튼, 라이트/다크 자동. 일본어 페이지는 빌드 시 Noto Sans JP로 바뀝니다.
- 제품 사진은 크레인 벨 공식 컷(1680 x 1500, 흰 바탕)이라 1:1 흰 바탕에 잘리지 않게(contain) 놓고, 히어로의 제품 슬라이드는 `light` 클래스로 흰 무대입니다. 포인트 컬러는 황동(#a8834a)으로 포커스 표시에만 씁니다.
- 헤더 로고는 글자 워드마크입니다. 공식 로고는 검정 상자 안의 흰 글자라 단색으로 칠하면 상자가 됩니다. 투명 배경 로고 파일을 받으면 `images/logo.png`로 넣고 헤더를 이미지로 바꾸면 됩니다.
- 자바스크립트가 꺼져 있어도 본문이 보이도록 등장 모션은 `html.js`일 때만 적용합니다.
- `index.src.html` 편집용 한국어 원본. 모델 비교표와 마감 표는 `{{MODEL_TABLE}}`, `{{FINISH_TABLE}}` 자리에 빌드 시 채워집니다 (`tools/build.py` 안의 MODELS, FINISHES).
- `en/index.html`, `ja/index.html` 영어 · 일본어 페이지 (빌드로 생성, 직접 수정하지 않음)
- `i18n/tr_source.py` 한국어 · 영어 · 일본어 번역 묶음, `en.json` · `ja.json`은 여기서 생성. 이미지 대체 텍스트(크레인 {모델} {마감})와 마감 표의 컬러 칩 줄은 FINISH · MODEL 사전으로 자동 번역됩니다.
- `404.html` 하위 주소(/ene, /mini-suzu, /mini-karen, /riten, /finish, /build, /dealers 등)를 섹션으로 연결
- `.github/image-manifest.txt` + `fetch-images.yml` 크레인 벨 공식 사이트(cranebellco.com) 이미지 이전용 워크플로

## 처음 올릴 때
1. 저장소 `sereno-kwon/cranebell` main에 푸시하면 `fetch-images.yml`이 매니페스트의 이미지 33개를 받아 `images/`에 커밋합니다.
2. 배포: Cloudflare Pages(저장소 연결, 빌드 명령 없음, 출력 폴더 `/`) 또는 GitHub Pages(main / root).
3. 도메인 DNS에 `cranebell` CNAME 레코드를 추가합니다. CNAME 파일은 이미 들어 있습니다.
4. 파비콘은 별도로 넣어야 합니다: `images/favicon-48.png`, `images/favicon-96.png`, `images/apple-touch-icon.png`(180px), `images/logo-512.png`.
5. 구글 서치 콘솔 · 네이버 서치어드바이저에 사이트를 등록하고 `sitemap.xml`을 제출합니다. 네이버 소유 확인 HTML 파일은 루트에 넣으면 됩니다.

## 이미지
- 제품 컷과 히어로 · 브랜드 사진은 cranebellco.com 공식 이미지입니다. 라이프스타일 사진이 없어 제품 컷 중심으로 구성했습니다.
- 루비에서 직접 찍은 사진(파일명 규칙 rubi-cranebell-lifestyle-상황-숫자)이 생기면 `images/brand/`, `images/hero/01.jpg`에 덮어쓰는 것을 권합니다.
- 미니 스즈 · 미니 카렌은 루비 취급 사양인 다이캐스트 마운트(22.2 · 25.4mm) 컷을 씁니다.
- 매니페스트를 고쳐 main에 푸시하면 Actions가 다시 받습니다. 이미 받은 파일은 건너뛰므로 교체할 때는 파일을 지우거나 새 파일명으로 추가합니다.

## 문구 수정과 번역
1. `index.src.html`의 한국어 문구를 고칩니다.
2. `python3 tools/build.py` → `python3 i18n/extract.py` 로 `ko.json`을 갱신합니다.
3. 바뀐 문장을 `i18n/tr_source.py`에서 같은 한국어 키로 고치거나 (한국어, 영어, 일본어)로 추가하고 `python3 i18n/tr_source.py`.
4. 다시 `python3 tools/build.py`. 번역되지 않은 문장이 있으면 목록으로 알려줍니다.

빌드에는 `beautifulsoup4`가 필요합니다.

## 링크
- 헤더 Shop, "루비워크샵에서 보기" 버튼: `https://rubiworkshop.com/brand-cranebell`
- 리튼 벨, 거래처 타일: `https://rubisupply.com/cranebell`
- 거래처 문의: 루비서플라이 02-516-8465, 카카오톡 채널 `https://pf.kakao.com/_NFnBj/chat`
- 푸터 Instagram: `https://www.instagram.com/rubi.workshop`

## 한글 표기
크레인 벨(Crane Bell Co.), 이네 벨(E-ne Bell), 미니 스즈 벨(Mini Suzu Bell), 미니 카렌 벨(Mini Karen Bell), 리튼 벨(Riten Bell, 리텐 아님). 마감: 크롬 플레이트, 올 크롬 플레이트, 폴리시드 실버, 매트 실버, 폴리시드 골드, 매트 골드, 코퍼, 브러시드 코퍼, 브라운, 네오 블랙, 스텔스 블랙, 올 스텔스 블랙.

## 출처
- 스펙(돔 지름, 마운트, 핸들바 규격, 소재, 무게): cranebellco.com 모델별 Specs (2026-11 확인)
- 취급 모델 · 마감: rubiworkshop.com/brand-cranebell, rubisupply.com/cranebell (2026-11 확인)
- 마감 선택 · 빌드 매칭 문구: rubisupply.com/cranebell 브랜드 마인드맵
