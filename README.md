# 생산운영과 공장관리

공장관리기술사 **출제기준(필기, 2027.01.01~2030.12.31)**의 `주요항목 → 세부항목 → 주제(목차) → 기출문제` 구조로 만든 MkDocs 교재입니다.
제63회~제139회 기출 867문항을 세부항목·주제별로 분류하고, 34개 세부항목 모두에 학습 내용(이론·비교표·도식·계산 기출 풀이·답안 작성 포인트·결론 예)과 페이지별 **답안 작성 예시**(25점 답안 구성)를 작성했습니다. 답안 구성법은 `docs/appendix/answer-guide.md`(답안 작성 가이드)에 정리했습니다. 가정을 두고 푼 부분과 확인이 필요한 정의는 `docs/appendix/review.md`(확인 필요 항목)에 모아 두었습니다.

## 구조

```
docs/
├── index.md                      # 홈: 출제기준과 기출 분포
├── 01-production-strategy/       # 1. 생산전략
│   ├── index.md                  #    장 개요(세부항목별 기출 수)
│   ├── 01-competitive-strategy.md#    1.1 경쟁우위 생산전략 (출제 경향 · 목차 · 주제별 기출)
│   └── ...
├── ... 02 ~ 07                   # 2~7 주요항목
└── appendix/
    ├── answer-guide.md           # 답안 작성 가이드(직접 관리)
    ├── frequency.md              # 출제 빈도 분석
    ├── rounds.md                 # 회차별 기출 색인
    └── review.md                 # 확인 필요 항목(직접 관리)
data/questions.csv                # 기출문제 + 출제기준 분류(주요항목·세부항목)
scripts/generate_scaffold.py      # 뼈대 생성기(주제 정의·매칭 규칙 포함)
scripts/mkdocs.base.yml           # mkdocs 설정 원본 (mkdocs.yml은 생성물)
```

## 로컬 실행

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve                    # http://127.0.0.1:8000
```

## 내용 작성

- 각 세부항목 페이지의 학습 내용을 직접 수정·보완하면 됩니다. 새 출제기준 페이지를 추가하면 `!!! abstract "학습 내용 (작성 예정)"` 자리가 생성됩니다.
- 수식은 `\( ... \)`(인라인), `\[ ... \]`(블록)로 씁니다. 예: `\( EOQ = \sqrt{2DS/H} \)`

## 뼈대 재생성

```bash
python scripts/generate_scaffold.py          # 기존 세부항목 페이지는 보존, 색인·분석·nav만 갱신
python scripts/generate_scaffold.py --force  # 모든 페이지를 새로 생성 (작성한 본문이 지워짐)
```

새 회차 기출을 추가하거나 분류를 바꾸려면 `data/questions.csv`를 고친 뒤 재생성합니다.
mkdocs 설정은 `scripts/mkdocs.base.yml`에서 수정합니다(`mkdocs.yml`은 덮어써짐).

## 배포 (GitHub Pages)

`main`에 push하면 `.github/workflows/deploy.yml`이 `gh-pages` 브랜치로 배포합니다.
저장소 **Settings → Pages → Source: Deploy from a branch → `gh-pages`** 로 한 번 설정하세요.
