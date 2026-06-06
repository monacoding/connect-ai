# md_convert

`manifest.json`의 PDF/텍스트 자료를 Markdown과 AI 학습용 JSONL로 변환합니다.

출력:
- `_company/suneung/markdown/*.md`
- `_company/suneung/datasets/suneung_learning.jsonl`

PDF 텍스트 추출에는 `pypdf`가 있으면 사용합니다.

```bash
python3 md_convert.py md_convert.json
```
