"""출제기준(주요항목-세부항목)과 분류된 기출문제(data/questions.csv)로 교재 뼈대를 생성한다.

- 세부항목 페이지: 출제 경향 + 목차(주제) + 주제별 관련 기출 + 작성 예정 자리
- 주요항목 index, 홈, 출제 빈도 분석, 회차별 기출 색인, mkdocs.yml nav

이미 존재하는 세부항목 페이지는 덮어쓰지 않는다(본문을 작성한 뒤 재실행해도 안전).
--force 를 주면 전부 다시 만든다. 색인/분석 페이지와 nav는 항상 갱신된다.

    python scripts/generate_scaffold.py [--force]
"""
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
FORCE = "--force" in sys.argv

# (번호, 주요항목명, 폴더, [(세부항목명, 파일, [(주제, 매칭정규식, 매칭우선순위)])])
# 주제는 화면 표시 순서대로 적고, 한 문항은 우선순위(작은 값 먼저)로 처음 매칭되는 주제 하나에만 들어간다.
# 어느 주제에도 매칭되지 않으면 '기타 관련 기출'로 모은다.
STANDARD = [
    (1, "생산전략", "01-production-strategy", [
        ("경쟁우위 생산전략", "01-competitive-strategy", [
            ("생산전략과 생산운영전략의 개념", r"생산전략|운영전략|생산정책|생산관리의 목표|생산관리 목표|의사결정|입력자료|장기경영|비젼", 9),
            ("경쟁우선순위와 경쟁우위 요소", r"경쟁우선|경쟁우위|경쟁능력|경쟁전략변수|주문적격|유연성|생산성과 목표|시간단축|시간은", 6),
            ("포터의 본원적 경쟁전략", r"포터|porter|Porter|저원가|차별화전략", 2),
            ("생산시스템 포지셔닝과 집중화 공장", r"포지셔닝|positioning|Focused|집중화 공장|공정중심|Wheelwright", 5),
            ("대량맞춤생산과 플랫폼 전략", r"Mass Custom|매스커스터|대량맞춤|Platform|플랫폼|Beach", 3),
            ("제품수명주기에 따른 생산전략", r"수명주기|라이프사이클|Life Cycle", 4),
            ("성과측정: BSC·KPI·CSF", r"BSC|Balanced|KPI|CSF|성과|평가지표|재무지표", 1),
            ("구조조정 전략(다운사이징·리엔지니어링)", r"다운사이징|Downsizing", 7),
        ]),
        ("생산구조와 방식(Layout)", "02-production-system-layout", [
            ("생산시스템의 유형과 발전(테일러·포드)", r"Taylor|테일러|포드|Ford|생산시스템의 5|생산시스템의 모형|단속생산|Variety|포지셔닝|공정중심", 7),
            ("주문 형태별 생산방식(MTS·ATO·MTO·ETO)", r"MTO|MTS|ATO|Make [Tt]o|Assemble|주문조립|납기에 따른|To Order|To Oder|생산전략의 기본", 5),
            ("공장입지 선정", r"입지|부지", 1),
            ("설비배치의 기본 유형", r"배치|레이아웃|Job Shop", 4),
            ("SLP·P-Q 분석·활동관련도", r"SLP|P-Q|활동관련도|From-To", 2),
            ("셀 생산·GT·U라인", r"셀|Cell|CMS|GT|그룹 ?테크|U자", 3),
            ("다품종 소량생산과 모듈 생산", r"다품종|Modular|모듈", 6),
        ]),
        ("구매와 외주전략", "03-purchasing-outsourcing", [
            ("구매관리와 구매방식", r"구매|MRO|Commodity|전략자재", 4),
            ("외주·아웃소싱 전략", r"외주|아웃소싱|Outsourcing", 3),
            ("수직적 통합과 자가생산·외주 결정", r"수직적 통합|자가생산", 1),
            ("공급자 관계관리(SRM·JIT II)", r"SRM|JIT", 2),
        ]),
        ("인력과 직무설계", "04-workforce-job-design", [
            ("조직구조와 조직 설계", r"조직|아메바|기종장|소사장|Project|팀|직능식|관리기능", 4),
            ("동기부여·리더십·조직행동", r"Maslow|Z 이론|이직|사기|직무만족|갈등|MBO", 1),
            ("직무설계와 다기능화", r"직무|다기능", 3),
            ("권한위양", r"권한", 2),
        ]),
        ("사업환경분석", "05-business-environment", [
            ("환경분석 기법(SWOT·5 Forces·BCG)", r"SWOT|Forces|산업구조|BCG|포트폴리오|Benchmark", 1),
            ("제품수명주기(PLC)", r"수명주기|수명의 주기|Life Cycle", 2),
            ("블루오션 전략", r"Blue|블루", 3),
            ("마케팅 믹스(4P)", r"4P|마케팅", 4),
            ("리스크 관리", r"Risk|리스크", 5),
            ("신규사업 기획", r"신규사업", 6),
        ]),
    ]),
    (2, "생산운영 및 물류관리", "02-operations-logistics", [
        ("수요예측과 일정계획", "01-forecasting-scheduling", [
            ("수요예측의 개요와 정성적 기법", r"수요예측|질적|수요에 영향|정성", 5),
            ("시계열 예측(이동평균·지수평활)", r"이동평균|지수평활|시계열|최소자승", 3),
            ("예측오차와 추적지표", r"추적|예측오차|예측치", 2),
            ("작업순서 결정과 우선순위 규칙", r"우선순위|SPT|작업순서|작업배정|스케줄|Scheduling|스케쥴", 4),
            ("다수 기계 일정계획(존슨·Petrov)", r"Johnson|존슨|Petrov|기계 1과", 1),
            ("일정계획 일반", r"일정계획|염색", 6),
        ]),
        ("프로세스 진도관리", "02-progress-control", [
            ("생산통제와 공정관리 기능", r"통제|진도|공정관리 기능", 4),
            ("생산기간(리드타임) 단축", r"리드타임|Lead|생산기간|납기", 3),
            ("공정대기의 원인과 대책", r"대기", 2),
            ("주문잔고 관리", r"잔고|Backlog", 1),
            ("예측생산 시스템의 관리 단계", r"예측생산", 0),
        ]),
        ("공급망 관리(SCM)", "03-scm", [
            ("SCM의 개념과 성과측정", r"SCM|Supply|공급사슬|공급망", 7),
            ("채찍효과", r"채찍|Bullwhip", 1),
            ("Push-Pull 공급체인", r"[Pp]ush|밀기", 2),
            ("신속대응(QR)과 애자일", r"QR|Quick|애자일|AGILE", 3),
            ("공급자 주도 재고(VMI·CRP·COCK)", r"VMI|CRP|COCK|Continuous", 4),
            ("물류 아웃소싱과 유통(3PL·크로스도킹·SPA·OMS)", r"3PL|크로스|SPA|OMS", 5),
            ("수요 불확실성과 제품가용성", r"불확실|가용성", 6),
        ]),
        ("물류관리(자재 및 재고관리)", "04-materials-inventory", [
            ("재고의 유형과 기능", r"유형|종류|분류법|보유 목적|주기재고", 6),
            ("경제적 주문량(EOQ·EPQ)", r"EOQ|EPQ|경제적|총 재고비용", 2),
            ("재고관리 시스템(정량·정기·Two-Bin)", r"정량|정기|Q시스템|[Tt][Ww][Oo]|[Bb]in|BIN|독립|최적 재고정책|재고관리 ?시스템|지표", 4),
            ("ABC 분석과 자재분류", r"ABC|자재분류", 3),
            ("자재소요계획(MRP)", r"MRP|자재소요|BOM", 1),
            ("창고·물류관리(WMS·RFID)", r"창고|WMS|RFID|물류|FIFO|선입선출", 5),
        ]),
        ("제조실행시스템(MES)", "05-mes", [
            ("MES의 개념과 기능", r"MES", 2),
            ("MOM과 현장 데이터 수집", r"MOM|데이터", 1),
        ]),
    ]),
    (3, "공정관리", "03-process-control", [
        ("생산계획수립", "01-production-planning", [
            ("총괄생산계획(APP)", r"총괄", 2),
            ("기준생산계획(MPS)", r"MPS|대일정", 1),
            ("생산능력 계획(CRP 포함)", r"능력|용량|CRP", 3),
            ("생산계획·통제 체계", r"생산계획|계획부문|평준화|수요가 계절", 4),
        ]),
        ("공정설계", "02-process-design", [
            ("공정설계와 공정 결정 요인", r"공정설계|Process planning|공정을 결정|생산공정을 선정|프로세스 결정|공정순서|Routing", 3),
            ("피치타임·사이클타임", r"피치|Pitch|사이클 타임", 2),
            ("라인밸런싱과 라인 편성", r"라인|[Ll]ine|밸런|작업요소", 1),
        ]),
        ("작업계획수립", "03-work-planning", [
            ("작업 분할과 작업계획", r"작업을 분할", 1),
            ("인간-기계 작업분석(Man-Machine Chart)", r"Man-Machine|연합|자동기계|Unload", 2),
        ]),
        ("표준작업관리", "04-standard-work", [
            ("표준과 표준화", r"표준", 3),
            ("5S·3정", r"5S|6S|3정", 1),
            ("눈으로 보는 관리", r"눈으로", 2),
        ]),
        ("설비보전관리", "05-maintenance", [
            ("설비보전의 유형과 보전조직", r"보전 ?유형|보전 ?조직|예지|직접기능|사전보전|설비보전에 대하여|TBM", 6),
            ("TPM과 자주보전", r"TPM|자주보전|Total Pro", 2),
            ("설비 로스와 설비종합효율(OEE)", r"로스|[Ll]oss|6대 손실|종합 ?효율|종합설비 ?효율|설비효율|가동[률율]|가동현황", 3),
            ("고장과 욕조곡선", r"욕조|Bathtub|고장곡선|고장률|고장대책|고장의|열화|파국|고장손실|윤활|설비고장", 7),
            ("신뢰성·보전성·가용도(RAM)", r"신뢰|MTBF|MTTR|MTTF|가용|Availability|유용성|용장|Reliab|고장강도|고장도수|결합된 시스템", 5),
            ("보전비용과 보전 경제성", r"비용|경제성", 4),
            ("PM 분석", r"PM\s?\(Phen|PM분석", 1),
        ]),
        ("공정개선", "06-process-improvement", [
            ("7대 낭비와 로스", r"낭비|대기", 2),
            ("준비교체 시간 단축(SMED)", r"준비|로트 사이즈", 1),
            ("병목·라인 개선과 공정수 감축", r"병목|라인|Tack|공정수|컨설팅|작업장", 3),
        ]),
    ]),
    (4, "설비관리", "04-facility-management", [
        ("설비계획 및 관리", "01-equipment-planning", [
            ("설비 갱신과 교체분석(MAPI)", r"MAPI", 1),
            ("설비 소요량 계획", r"기계대수|설비계획", 2),
            ("치공구 관리", r"치공구", 3),
            ("설비관리 시스템과 리스크 관리", r"전문가|Risk", 4),
        ]),
        ("자재취급 및 운반관리", "02-material-handling", [
            ("운반관리의 원칙과 활성지수", r"운반|활성지수", 1),
            ("보관과 오더피킹", r"보관|피킹|Picking", 2),
            ("포장·유닛로드·수배송", r"포장|Unit|TOFC|수송|용기", 3),
            ("운반설비(AGV)", r"AGV", 4),
            ("물품 취급방법 설계", r"취급", 5),
        ]),
        ("환경관리 및 안전관리", "03-environment-safety", [
            ("환경친화 생산과 친환경 설계", r"환경|DFE|LCA|RoHS", 2),
            ("환경·안전보건경영시스템(ISO 14001·45001)", r"ISO", 1),
            ("설비 안전설계(Fool Proof·Interlock·위험점)", r"Fool|위험점|Interlock", 3),
        ]),
        ("시설 및 유틸리티관리", "04-facilities-utilities", [
            ("공장 시설계획", r"$^", 1),
            ("유틸리티(전력·용수·공기·스팀) 관리", r"$^", 2),
            ("에너지 관리와 효율화", r"$^", 3),
        ]),
        ("공장자동화 기술", "05-factory-automation", [
            ("공장자동화의 개념과 유형", r"자동화", 3),
            ("유연생산시스템(FMS)·DNC", r"FMS|유연|DNC", 1),
            ("가상제조·SCADA", r"VMS|가상|SCADA", 2),
        ]),
    ]),
    (5, "작업관리와 성과측정", "05-work-measurement", [
        ("작업방법 및 시간 연구", "01-method-time-study", [
            ("작업측정과 표준시간", r"표준시간|정미시간|작업 소요시간|시간에 관한 용어|시간연구|Standard Time|표준작업시간", 7),
            ("여유시간과 여유율", r"여유", 5),
            ("레이팅(수행도 평가)", r"레이팅|Rating|Raing", 4),
            ("워크샘플링", r"샘플링|Sampling|관측 회수", 2),
            ("PTS법(MTM·WF·RWF·MODAPTS)", r"MTM|WF|Work Factor|RWF|MODAPTS", 3),
            ("동작연구와 서블릭", r"동작|서블릭|써블릭|Therblig", 6),
            ("학습곡선", r"학습|LCF|Learning", 1),
            ("과학적 관리법", r"Taylor", 8),
        ]),
        ("프로세스 분석과 개선", "02-process-analysis", [
            ("개선의 원칙(ECRS·5W1H)", r"ECRS|E\.C\.R|개선의 기본원칙|5W1H", 1),
            ("공정분석 기법과 도표", r"공정분석|공정기호|도표|분석하기 위한|경로분석|4W|SIPOC|가치흐름|Value Stream|8대 프로세스|프로세스와 시스템", 2),
            ("아이디어 발상과 문제해결 기법", r"브레인|희망열거|KJ|문제해결|문제 해결|Gordon|고든", 3),
            ("Less Engineering과 제안제도", r"Less|제안", 4),
            ("IE 기법의 현장 적용", r"IE|원가절감과 납기", 5),
        ]),
        ("생산성 및 안전관리", "03-productivity-safety", [
            ("생산성의 개념과 측정", r"생산성|원단위|수율|실동|효율성|경영효율|노동장비율|부가가치", 3),
            ("산업재해 지표(도수율·강도율)", r"도수율|재해|강도율", 1),
            ("인적 요인과 생산 로스", r"사람|작업 수행도|임금", 2),
        ]),
        ("품질관리", "04-quality-management", [
            ("품질경영·TQM·ISO 9000", r"TQM|ISO|품질경영|Crosby|Garvin|프로세스 접근|ZD|Hidden", 9),
            ("품질비용(COQ)", r"[Cc]ost|코스트|비용|COPQ", 7),
            ("통계적 공정관리(관리도·공정능력)", r"관리도|공정능력|SPC|F검증|Ftest|부적합수|AQL|QC 7|품질관리 7|신 QC|특성요인도", 8),
            ("측정시스템분석(MSA·Gage R&R)", r"R ?& ?R|측정|재현성|MSA", 4),
            ("6시그마(DMAIC·DMADV·DFSS)", r"시그마|σ|DMAIC|DMADV|DFSS|Rolled|누적수율|CTQ", 6),
            ("다구찌 품질공학과 강건설계", r"Taguchi|다구찌|강건|Robust|공차설계|허용차|손실함수", 5),
            ("카노 모델", r"Kano|카노", 1),
            ("FMEA·FTA·실수방지", r"FMEA|FMECA|FTA|Fault|Fool", 3),
            ("제조물책임(PL)", r"\bPL\b|제조물|제품책임|Product liab", 2),
        ]),
    ]),
    (6, "원가관리 및 경제성공학", "06-cost-engineering-economy", [
        ("사업성분석", "01-feasibility", [
            ("투자 경제성 평가(NPV·IRR·회수기간)", r"투자|현금흐름|회수|경제성|MARR|내용[년연]수|LCC|적금|사업성", 5),
            ("손익분기점(BEP) 분석", r"손익분기|BEP|한계이익", 3),
            ("감가상각", r"감가상각", 1),
            ("경제성 분석의 비용 개념(매몰·기회비용)", r"매몰|기회비용|초기비용", 2),
            ("사업 타당성 분석", r"타당성", 4),
        ]),
        ("원가관리", "02-cost-management", [
            ("원가의 개념과 구성", r"원가의 본질|구성|비용과 원가|원가에서는|직접비|원가 종류", 6),
            ("원가계산(표준·종합·ABC·간접비 배부)", r"표준원가|종합원가|ABC|Activity|간접비|준평균|원단위|실제원가", 4),
            ("원가절감", r"절감|고정비|원가관리의 중요", 5),
            ("목표원가", r"목표원가|Target", 2),
            ("관리회계(공헌이익·쓰루풋 회계)", r"공헌이익|Throughput|기회원가|COCK", 3),
            ("재무제표", r"재무|대차대조표|무형", 1),
        ]),
        ("가치공학", "03-value-engineering", [
            ("VE의 개념과 기본원칙", r"VE|VA|가치", 3),
            ("기능분석과 가치 평가", r"기능", 1),
            ("VE 추진절차", r"추진|절차|과정", 2),
        ]),
        ("경영과학(OR)", "04-operations-research", [
            ("선형계획법(LP)", r"선형|LP|Liner", 3),
            ("수송·할당 문제", r"수송|Transport|할당|3대의 기계", 4),
            ("대기행렬 이론", r"대기행렬|Queue|M/M/1", 1),
            ("의사결정 이론(불확실성하 의사결정·AHP)", r"의사결정|Wald|Laplace|AHP|ANP|확률|불확실", 5),
            ("프로젝트 관리와 PERT/CPM", r"PERT|CPM|Critical|네트워크|[Nn]etwork|프로젝트|CCM|AOA|Project Management", 2),
            ("시뮬레이션과 DEA", r"시뮬레이션|DEA", 6),
        ]),
    ]),
    (7, "생산지원기술 및 기타", "07-support-technology", [
        ("정보화활용기술(스마트팩토리 및 AI 등)", "01-it-smart-factory", [
            ("경영정보시스템(ERP·SCM·CRM·KMS)", r"ERP|CRM|KMS|DSS|SIS|지식|정보화|Biz|전자화폐|소셜|CPC|생산정보", 6),
            ("스마트공장", r"스마트|Smart|ICBM|CPS|DX|AX", 4),
            ("사물인터넷과 센서 네트워크", r"IoT|USN|EDI", 3),
            ("인공지능과 기계학습", r"인공지능|AI|기계학습|Machine|딥러닝", 2),
            ("가상현실·증강현실", r"가상현실|증강|virtual", 1),
            ("APS(Advanced Planning & Scheduling)", r"APS", 5),
        ]),
        ("제품개발기술", "02-product-development", [
            ("신제품 개발 프로세스", r"신제품|개발과정|제품개발|제품의 디자인|소비자 needs|MGPP|타당성|PLC|라이프 사이클|R&BD", 9),
            ("품질기능전개(QFD·HOQ)", r"QFD|품질의 집|HOQ", 1),
            ("동시공학(CE)", r"동시|Concurrent|\bCE\b", 2),
            ("제조용이성 설계(DFM)와 원가지향 설계", r"DFM|용이성|원가절감을 위한 설계|A전자", 3),
            ("모듈러 설계·VRP·제품 플랫폼", r"모듈|VRP|Variety|플랫폼|Platform|차별화 지연|Benetton", 4),
            ("DFSS와 설계 검토", r"DFSS|Design Review|Design Score", 5),
            ("창의적 설계 기법(TRIZ·Pugh·디자인 사고)", r"TRIZ|Pugh|디자인사고|Design Thinking", 6),
            ("제품 데이터·수명주기관리(PDM·PLM·BOM)", r"PDM|PLM|BOM", 7),
            ("기타 설계 기법(유니버설 디자인·역설계)", r"Universal|Reverse", 8),
        ]),
        ("서비스운영관리", "03-service-operations", [
            ("서비스 운영의 특성과 설계", r"분류|제조와 서비스|서비스 ?시스템|서비스설계|설계", 4),
            ("서비스 품질(SERVQUAL·서비스 격차)", r"SERVQUAL|서비스품질|격차|고객만족", 1),
            ("고객접점관리(MOT)", r"MOT|Moment", 2),
            ("수익관리(PRM)", r"PRM|Revenue", 3),
        ]),
        ("생산혁신기술", "04-production-innovation", [
            ("도요타 생산방식과 JIT", r"도요타|TPS|JIT|간판|Kanban|Autonomation|JIDOKA|동기생산|택트|흐름생산", 3),
            ("린 생산과 린 6시그마", r"Lean|린", 2),
            ("제약이론(TOC·OPT·DBR)", r"TOC|제약|OPT|DBR|Drum|Goal|골드렛|병목|Bottleneck|Throughput|쓰루풋|Buffer", 1),
            ("혁신활동과 변화관리(BPR·TQM·카이젠)", r"TQM|혁신|BPR|변화관리|Lewin|컨설턴트|Kaizen|카이젠", 4),
        ]),
        ("공장관리 신기술 및 경향에 관한 사항", "05-trends", [
            ("ESG·지속가능경영·통상규제", r"ESG|지속가능|Sustain|RE100|CSR|윤리|IRA|무역규제", 1),
            ("미래 공장(등대공장·SDF·다크팩토리·자율공장)", r"등대|Software|Dark|자율|Digital Thread|Physical AI", 2),
            ("기술경영", r"기술의 종류", 3),
        ]),
    ]),
]

ETC = "기타 관련 기출"


def load_questions():
    with open(ROOT / "data" / "questions.csv", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["rnd"] = int(r["회차"].strip("제회"))
        r["m"] = int(r["주요항목"].split(".")[0])
        r["s"] = int(r["세부항목"].split(".")[0])
    return rows


def md_escape(text):
    text = text.replace("\\", "\\\\").replace("*", "\\*").replace("_", "\\_")
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    return re.sub(r"^(\s*)([#+-])", r"\1\\\2", text, flags=re.M)


def assign_topics(questions, topics):
    by_priority = sorted(range(len(topics)), key=lambda i: topics[i][2])
    groups = defaultdict(list)
    for q in questions:
        hit = next((i for i in by_priority if re.search(topics[i][1], q["시험문제"])), None)
        groups[topics[hit][0] if hit is not None else ETC].append(q)
    return groups


def q_label(q):
    return f"제{q['rnd']}회({q['연도']}) {q['교시']} {q['번호']}번"


def question_item(q):
    lines = q["시험문제"].strip().split("\n")
    out = [f"- **{q_label(q)}** · {q['배점']}점  ", f"  {md_escape(lines[0])}"]
    if len(lines) > 1:
        out.append("")
        out.append('    ??? quote "문제 전문"')
        out.append("")
        out += [f"        {md_escape(l)}  " for l in lines]
    return "\n".join(out)


def rounds_text(qs):
    return ", ".join(f"{r}회" for r in sorted({q["rnd"] for q in qs}))


def trend_summary(qs, all_rounds):
    if not qs:
        return "현행 기출 데이터(제63회~제139회)에는 이 세부항목으로 분류된 문항이 없습니다. 새 출제기준(2027~)에 추가된 영역이므로 기본 개념 위주로 대비합니다."
    short = sum(1 for q in qs if q["교시"] == "1교시")
    recent = [r for r in all_rounds[-10:]]
    recent_n = sum(1 for q in qs if q["rnd"] in recent)
    last = max(q["rnd"] for q in qs)
    return (f"총 **{len(qs)}문항** 출제 (1교시 단답형 {short} · 2~4교시 논술형 {len(qs) - short}) · "
            f"최근 10개 회차({recent[0]}~{recent[-1]}회) {recent_n}문항 · 최근 출제 제{last}회")


def write(path, text, protect=False):
    if protect and path.exists() and not FORCE:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def build():
    qs = load_questions()
    all_rounds = sorted({q["rnd"] for q in qs})
    total = len(qs)
    nav = []
    home_rows = []
    freq_rows = []
    topic_stats = []
    section_link = {}
    skipped = 0

    for m, mname, mdir, subs in STANDARD:
        m_qs = [q for q in qs if q["m"] == m]
        m_nav = [{f"{m}. {mname}": f"{mdir}/index.md"}]
        m_rows = []
        for s, (sname, sfile, topics) in enumerate(subs, 1):
            s_qs = sorted([q for q in m_qs if q["s"] == s], key=lambda q: (q["rnd"], q["교시"], int(q["번호"])))
            groups = assign_topics(s_qs, topics)
            names = [t[0] for t in topics] + ([ETC] if groups.get(ETC) else [])
            num = f"{m}.{s}"
            rel = f"{mdir}/{sfile}.md"
            section_link[(m, s)] = rel
            m_nav.append({f"{num} {sname}": rel})
            m_rows.append((num, sname, f"{sfile}.md", len(s_qs), groups, names))
            freq_rows.append((m, mname, num, sname, rel, s_qs))

            p = [f"# {num} {sname}", "",
                 f'!!! info "출제기준"', f"    **{m}. {mname}** › **{s}. {sname}**", "",
                 "## 출제 경향", "", trend_summary(s_qs, all_rounds), ""]
            p += ["| 주제 | 출제 수 | 출제 회차 |", "|---|:-:|---|"]
            for i, name in enumerate(names, 1):
                g = groups.get(name, [])
                p.append(f"| {num}.{i} {name} | {len(g)} | {rounds_text(g) or '-'} |")
                topic_stats.append((len(g), f"{num}.{i} {name}", rel))
            p += ["", "## 목차", ""]
            for i, name in enumerate(names, 1):
                p.append(f"{i}. [{name}](#t{num.replace('.', '')}-{i})")
            p.append("")
            for i, name in enumerate(names, 1):
                g = groups.get(name, [])
                p += [f"## {num}.{i} {name} {{#t{num.replace('.', '')}-{i}}}", "",
                      '!!! abstract "학습 내용 (작성 예정)"',
                      "    - 핵심 개념:", "    - 주요 이론·공식:", "    - 답안 작성 포인트:", ""]
                if g:
                    p += [f'??? example "관련 기출 {len(g)}문항 ({rounds_text(g)})"', ""]
                    p += ["\n".join("    " + l if l else "" for l in question_item(q).split("\n")) for q in g]
                    p.append("")
                else:
                    p += ["*관련 기출 없음*", ""]
            if not write(DOCS / rel, "\n".join(p), protect=True):
                skipped += 1

        idx = [f"# {m}. {mname}", "",
               f"이 장은 출제기준 주요항목 **{m}. {mname}**의 세부항목 {len(subs)}개로 구성됩니다. "
               f"기출 {len(m_qs)}문항(전체의 {len(m_qs) / total:.1%})이 이 장에 해당합니다.", "",
               "| 세부항목 | 기출 수 | 주요 주제(출제 수) |", "|---|:-:|---|"]
        for num, sname, f, n, groups, names in m_rows:
            top = sorted(((len(groups.get(x, [])), x) for x in names if x != ETC), reverse=True)[:3]
            idx.append(f"| [{num} {sname}]({f}) | {n} | " + ", ".join(f"{x}({c})" for c, x in top if c) + " |")
        write(DOCS / mdir / "index.md", "\n".join(idx) + "\n")
        home_rows.append((m, mname, mdir, len(m_qs), m_rows))
        nav.append({f"{m}. {mname}": m_nav})

    # 홈
    h = ["# 공장관리기술사 기출 중심 교재", "",
         "공장관리기술사 **출제기준(필기, 적용기간 2027.01.01~2030.12.31)**의 주요항목·세부항목 순서로 구성한 학습 교재입니다. "
         f"제{all_rounds[0]}회~제{all_rounds[-1]}회 기출 **{total}문항**을 세부항목과 주제별로 분류해 각 장에 실었습니다.", "",
         '!!! tip "이 교재 사용법"',
         "    1. 각 세부항목 페이지 맨 위 **출제 경향** 표에서 자주 나오는 주제를 먼저 확인합니다.",
         "    2. **목차**의 주제별로 학습 내용을 정리하고, 아래 **관련 기출**을 펼쳐 답안을 연습합니다.",
         "    3. 회차별로 복습하려면 [회차별 기출 색인](appendix/rounds.md)을, 우선순위를 보려면 [출제 빈도 분석](appendix/frequency.md)을 봅니다.", "",
         "## 출제기준과 기출 분포", "", "| 주요항목 | 세부항목 | 기출 수 |", "|---|---|:-:|"]
    for m, mname, mdir, n, m_rows in home_rows:
        for k, (num, sname, f, sn, _, _) in enumerate(m_rows):
            first = f"[**{m}. {mname}**]({mdir}/index.md) ({n})" if k == 0 else ""
            h.append(f"| {first} | [{num} {sname}]({mdir}/{f}) | {sn} |")
    h += ["", "## 시험 정보", "",
          "- 검정방법: 단답형/주관식 논문형, 400분(1교시당 100분)",
          "- 1교시: 단답형 13문항 중 10문항 선택(문항당 10점) · 2~4교시: 논술형 6문항 중 4문항 선택(문항당 25점)",
          "- 면접: 구술형 15~30분 내외 (필기 주요항목 + 기술자로서 품위 및 자질)", ""]
    write(DOCS / "index.md", "\n".join(h))

    # 출제 빈도 분석
    f = ["# 출제 빈도 분석", "", f"제{all_rounds[0]}회~제{all_rounds[-1]}회 기출 {total}문항 기준입니다.", "",
         "## 세부항목별 출제 수", "", "| 순위 | 세부항목 | 기출 수 | 비율 | 최근 10개 회차 |", "|:-:|---|:-:|:-:|:-:|"]
    recent = set(all_rounds[-10:])
    for i, (m, mname, num, sname, rel, s_qs) in enumerate(sorted(freq_rows, key=lambda x: -len(x[5])), 1):
        f.append(f"| {i} | [{num} {sname}](../{rel}) | {len(s_qs)} | {len(s_qs) / total:.1%} | "
                 f"{sum(1 for q in s_qs if q['rnd'] in recent)} |")
    f += ["", "## 자주 출제된 주제 Top 30", "", "| 순위 | 주제 | 기출 수 |", "|:-:|---|:-:|"]
    for i, (n, name, rel) in enumerate(sorted([t for t in topic_stats if ETC not in t[1]], key=lambda t: -t[0])[:30], 1):
        f.append(f"| {i} | [{name}](../{rel}) | {n} |")
    write(DOCS / "appendix" / "frequency.md", "\n".join(f) + "\n")

    # 회차별 색인
    r = ["# 회차별 기출 색인", "", "각 문항이 교재의 어느 세부항목에 실려 있는지 보여줍니다.", ""]
    for rnd in sorted(all_rounds, reverse=True):
        rq = sorted([q for q in qs if q["rnd"] == rnd], key=lambda q: (q["교시"], int(q["번호"])))
        r += [f'??? note "제{rnd}회 ({rq[0]["연도"]}년) · {len(rq)}문항"', "",
              "    | 교시 | 번호 | 문제 | 세부항목 |", "    |:-:|:-:|---|---|"]
        for q in rq:
            stem = md_escape(q["시험문제"].split("\n")[0]).replace("|", "\\|")
            r.append(f"    | {q['교시']} | {q['번호']} | {stem} | [{q['m']}.{q['s']}](../{section_link[(q['m'], q['s'])]}) |")
        r.append("")
    write(DOCS / "appendix" / "rounds.md", "\n".join(r))

    nav = [{"홈": "index.md"}] + nav + [{"부록": [{"출제 빈도 분석": "appendix/frequency.md"},
                                                {"회차별 기출 색인": "appendix/rounds.md"}]}]
    write_mkdocs_yml(nav)
    print(f"generated: {total} questions, {len(freq_rows)} sections" + (f", kept {skipped} existing pages" if skipped else ""))


def nav_yaml(items, indent=2):
    out = []
    for it in items:
        (k, v), = it.items()
        if isinstance(v, list):
            out.append(" " * indent + f"- \"{k}\":")
            out += nav_yaml(v, indent + 4)
        else:
            out.append(" " * indent + f"- \"{k}\": {v}")
    return out


def write_mkdocs_yml(nav):
    base = (ROOT / "scripts" / "mkdocs.base.yml").read_text(encoding="utf-8")
    write(ROOT / "mkdocs.yml", base.rstrip() + "\n\nnav:\n" + "\n".join(nav_yaml(nav)) + "\n")


if __name__ == "__main__":
    build()
