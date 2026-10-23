# FITFORM — Codex 개발용 소스

첨부 레퍼런스의 큰 공간 사진, 대형 타이포그래피, 아이보리·웜 브라운, 넓은 여백을 유지한 가구 플래너입니다. 추천 제품은 IKEA 한국 공식 판매 페이지에서 확인한 53종으로 바꾸었습니다. 새 버전은 사이트에 배포하지 않았습니다.

## 바로 실행하기

Node.js 20 이상을 사용하세요. 외부 npm 의존성이 없어 설치 과정은 없습니다.

```bash
npm run dev
```

브라우저에서 `http://localhost:5173`을 엽니다. 파일을 더블 클릭하지 말고 서버를 실행하세요. ES 모듈을 사용합니다.

```bash
npm test
npm run build
```

- `npm test`: 15개 검사
- `npm run build`: 정적 파일을 `dist/`에 복사. 배포하지 않습니다.

## GitHub → Codex 웹에서 시작하기

1. GitHub에서 `fitform`이라는 새 **Private** 저장소를 만듭니다. README를 추가해서 생성하면 다음 단계가 쉽습니다. 다른 게임·산 앱 저장소는 사용하지 않습니다.
2. 받은 ZIP을 압축 해제합니다.
3. GitHub 저장소의 `Add file → Upload files`에서 **압축 해제한 fitform-codex 폴더 안의 내용물**을 올립니다. ZIP 파일 자체나 상위 폴더 통째로 올리지 마세요. 최상위에 `package.json`, `AGENTS.md`, `CODEX_HANDOFF.md`, `public/`, `scripts/`, `tests/`, `docs/`가 보여야 합니다. README는 이 버전으로 교체해도 됩니다.
4. Codex의 GitHub 연결에 새 저장소 접근을 허용하고 이 저장소를 선택합니다. Cloud 환경을 새로 만드는 화면이면 해당 저장소를 선택해 준비·검사를 완료하고 환경을 활성화합니다.
5. 아래 지시문으로 첫 작업을 시작합니다.

```text
AGENTS.md와 CODEX_HANDOFF.md를 읽고 작업해줘.
기존 아이보리·웜 브라운 디자인과 사진·타이포그래피·여백을 유지해.
먼저 npm test와 npm run build를 실행하고 실제 브라우저에서 데스크톱·모바일 동작을 확인해줘.
IKEA 53종, 예산 필터, 가격순 정렬, 저장·비교 기능을 점검하고 관찰된 문제만 수정해줘.
키 기반 예시 추정을 검증된 공식 추천처럼 표현하지 말고 국가별 보정도 임의로 만들지 마.
수정은 새 브랜치에서 하고 테스트 결과와 남은 데이터 검증 과제를 설명하는 PR을 준비해줘.
자동 병합과 사이트 배포는 하지 마.
```

공식 흐름: https://learn.chatgpt.com/docs/cloud
화면 이름은 사용하는 Codex 버전과 환경에 따라 달라질 수 있습니다.

## Codex 앱/IDE에서 시작하기

압축 해제한 `fitform-codex` 폴더를 프로젝트로 열고 위 지시문을 사용합니다. 이어 GitHub 저장소를 생성하거나 연결하고 커밋·푸시를 요청할 수 있습니다. 연결 대상은 별도 `fitform` 저장소입니다. ZIP에는 예전 Sites의 Git 이력·배포 설정·자격증명이 들어 있지 않습니다.

## 주요 파일

| 파일 | 역할 |
|---|---|
| `public/index.html` | 화면 구조와 입력 폼 |
| `public/style.css` | 유지해야 할 기존 시각 디자인 |
| `public/app.js` | 필터·저장·비교·인쇄 및 화면 동작 |
| `public/products.mjs` | 실제 앱이 읽는 IKEA 가격·치수·출처 목록 |
| `public/model.mjs` | 검토용 추정식과 치수 교집합 계산 |
| `docs/products.json` | 인수인계 시점의 제품 목록 스냅샷 |
| `docs/DATA_NOTES.md` | 제품별 근거와 검증 한계 |
| `docs/design-references/` | 사용자가 제공한 디자인 참고 이미지 |
| `CODEX_HANDOFF.md` | 다음 개발자의 구체적인 작업 지침 |

제품 정보 수정은 `public/products.mjs`를 기준으로 진행하고 `docs/products.json`도 함께 갱신하세요.

## 완료한 검증과 한계

모델·입력 경계·필터·가격 정렬·제품 사양·파일 참조·개발 서버에 대한 검사 15개와 빌드를 통과했습니다. Chromium에서 1440/768/390 px의 제품 표시, 필터·정렬·저장·비교·입력 초기화 등 기본 동작을 확인했습니다. 신체 치수 입력 시 자동 필터하며 체크를 해제하면 전체 치수를 볼 수 있습니다. 상세 결과와 재현 방법은 `docs/QA.md`를 참고하세요.

현재 사람 치수 추정은 **검증 전 시제품 예시식**입니다. 국적·성별 보정 데이터는 연결하지 않았습니다. 실측값을 우선합니다. 라운지체어는 업무용 적합도로 자동 판정하지 않습니다. TROTTEN 전동 제품은 공식 높이 표기가 상충하여 자동 비교에서 제외합니다.

제품 사진은 해당 IKEA 한국 공식 제품 페이지의 사진과 동일한 파일을 사용합니다. 임의 도식이나 생성 이미지는 사용하지 않으며, 확인되지 않은 사진은 안내문으로 표시합니다. 기존 hero·공간 사진은 유지했습니다.

## 제품 수집·갱신

의자·책상·식탁·소파·라운지체어 53개 스냅샷이며 IKEA 전체 재고가 아닙니다. 사진 출처와 해시를 기록하고, 치수 확인이 가능한 의자·책상만 자동 추천합니다. `npm run catalog:refresh`로 재수집하고 `npm run test:import`로 수집기 검사를 실행합니다(Python 3.9 이상과 curl 필요). 매주 갱신 결과를 검토용 아티팩트로 만드는 GitHub Actions 정의를 추가했습니다. 병합·Actions 활성화 전에는 예약 실행되지 않습니다. 상세 범위와 한계는 `docs/CATALOG.md`를 참고하세요.

## Cloudflare Workers 미리보기 설정

루트 `wrangler.json`의 최상위 `previews: {}`로 `wrangler preview`를 활성화합니다. 이 저장소는 정적 사이트이므로 `assets.directory`는 `npm run build`가 만드는 `dist/`이며 별도 Worker 진입점이나 미리보기 바인딩은 필요하지 않습니다. `compatibility_date`는 Wrangler 4.152.0으로 검증한 `2026-10-19`입니다.

계정 ID·운영 Worker 이름·도메인·라우트는 이 파일에 새로 지정하지 않습니다. 기존 Cloudflare CI의 Worker 이름 설정을 유지하세요. 로컬에서 미리보기를 배포해야 할 때에는 기존 Worker 이름을 `npx wrangler preview --worker-name <기존-Worker-이름>`으로 전달합니다. `preview --name`은 미리보기 이름이고 운영 Worker 이름과 다른 옵션입니다. 이 명령은 실제 미리보기 배포를 실행하므로 이번 수정 검증에서는 실행하지 않았습니다.

이번 검증은 `npm test`, `npm run build`, 그리고 업로드하지 않는 `npx wrangler@4.152.0 deploy --dry-run --name fitform-config-check --outdir /tmp/fitform-wrangler-dry-run`으로 수행했습니다. `fitform-config-check`는 로컬 검사에만 사용하는 이름이며 배포 대상이 아닙니다. 별도 `env.preview`나 Pages 전용 설정은 추가하지 않았습니다.
