# source_ingest

공식/허가된 수능·모의평가 자료 URL 또는 로컬 파일을 `_company/suneung/sources`로 수집하고 `manifest.json`을 만듭니다.

안전 원칙:
- 한국교육과정평가원(KICE), 교육부, EBS 등 공식/허가된 자료 또는 직접 권리를 가진 파일만 입력합니다.
- 저작권 문구가 있는 문제지는 무단 복제·배포용으로 쓰지 않고, 내부 분석/검토 파이프라인의 원천 파일로만 보관합니다.
- 자동 크롤링이 아니라 사용자가 명시한 URL/파일만 처리합니다.

```bash
python3 source_ingest.py source_ingest.json
```
