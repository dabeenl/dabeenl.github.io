# dabeenl.github.io — 편집 가이드

이 사이트는 [Jekyll](https://jekyllrb.com)로 만들어져 있고, GitHub Pages가 `main` 브랜치에 커밋될 때마다 자동으로 빌드합니다.
파일을 고치고 커밋하면 1분 안팎으로 반영됩니다. 설치할 것은 없습니다. GitHub 웹사이트에서 파일을 열어 연필 아이콘으로 수정하고 **Commit changes**를 누르면 됩니다.

## 어디를 고치면 되나

| 하고 싶은 일 | 고칠 파일 |
| --- | --- |
| 논문·프리프린트 추가 | `_data/publications.yml` |
| 멤버 추가·졸업 처리 | `_data/members.yml`, `_data/alumni.yml` |
| 뉴스 한 줄 추가 | `_data/news.yml` |
| 연구과제·산학과제 | `_data/projects.yml` |
| 강의 목록 | `_data/courses.yml` (강의 페이지 자체는 지금처럼 `MA1407.html` 등을 직접 편집) |
| 소개 글, 연구 관심사 문단 | `index.md` |
| 연락처, 링크 버튼, 관심사 칩, 모집 안내 문구, 단체 사진 | `_data/profile.yml` |
| 공동연구자 목록 | `_data/collaborators.yml` |
| 상단 메뉴 | `_config.yml`의 `nav:` |
| 색·서체·간격 | `assets/css/style.css` 맨 위 `:root` |

`_layouts/`, `_includes/`는 페이지 뼈대입니다. 평소에는 건드릴 일이 없습니다.

## 논문 한 편 추가하기

`_data/publications.yml`의 맨 위(최신순)에 아래 블록을 붙여 넣고 내용을 바꿉니다.

```yaml
- title: "제목은 항상 큰따옴표 안에"
  authors: "Hong Gildong, Dabeen Lee*"
  year: 2027
  type: conference          # preprint | conference | journal
  venue: NeurIPS 2027
  detail: Conference on Neural Information Processing Systems
  links:
    - label: arXiv
      url: "https://arxiv.org/abs/XXXX.XXXXX"
    - label: pdf
      url: /new-paper.pdf     # 레포 루트에 올린 파일은 이렇게
```

- `authors`의 이름이 `members.yml`이나 `alumni.yml`에 있으면 자동으로 밑줄이 그어집니다. `*`는 교신저자, `(α–β)`는 알파벳 순 표시로 그대로 적습니다.
- `featured: true`를 추가하면 홈 화면 "Recent papers"에 보입니다(앞에서부터 3편).
- 첫 번째 링크가 제목 링크로 쓰입니다.
- 저널 논문에 학회 버전이 있으면 `conference:` 아래에 `venue`, `detail`, `links`를 적습니다. 저널 줄 아래에 Conference 줄로 표시되고, 학회 필터에서도 함께 보입니다.

## 멤버 추가하기

```yaml
- name: Hong Gildong
  program: Ph.D. student     # 비워 두면("") 표시 안 됨
  affiliation: SNU Math
  since: 2027
  homepage: "https://gildong.github.io"    # 없으면 줄 삭제
  photo: /assets/img/members/gildong.jpg   # 없으면 줄 삭제 → 이니셜 표시
```

졸업하면 `members.yml`에서 지우고 `alumni.yml`에 옮겨 적습니다(`now:`에 현재 소속을 적으면 함께 표시).

## 뉴스 추가하기

```yaml
- label: ICML 2027
  text: "*논문 제목* accepted. [링크 텍스트](https://...)도 됩니다."
```

## 자주 하는 실수

- **제목에 콜론(`:`)이나 따옴표가 있으면 반드시 큰따옴표로 감싸기.** 안 그러면 빌드가 실패합니다.
- 들여쓰기는 스페이스 2칸. 탭은 쓰지 않습니다.
- URL은 큰따옴표로 감싸는 편이 안전합니다(`?`, `#` 같은 문자 때문).
- 빌드가 실패하면 GitHub이 메일을 보내고, 사이트는 마지막으로 성공한 버전 그대로 남습니다. 레포의 **Actions** 탭이나 **Settings → Pages**에서 에러 메시지를 볼 수 있습니다. 대부분 YAML 따옴표 문제입니다.

## 로컬에서 미리보기 (선택)

Ruby가 설치되어 있다면 레포 폴더에서:

```
bundle install
bundle exec jekyll serve
```

그다음 http://localhost:4000 을 엽니다. 로컬 서버에서는 `/MA1407` 같은 확장자 없는 주소가 열리지 않을 수 있으니 `/MA1407.html`로 확인하세요(GitHub Pages에서는 둘 다 됩니다).

## 구조 메모

- 루트의 PDF, 강의 페이지(`*.html`), 노트북 파일은 그대로 복사되어 예전 주소 그대로 열립니다.
- 예전 홈 화면은 `_archive/index.html`에 보관되어 있습니다(밑줄로 시작하는 폴더는 사이트에 올라가지 않습니다).
