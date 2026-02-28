import streamlit as st
import xml.etree.ElementTree as ET
import io

# --- Core Logic / 핵심 변환 로직 ---
def parse_fcp_time(time_str):
    if not time_str: return 0.0
    time_str = time_str.replace('s', '')
    if '/' in time_str:
        try:
            num, den = map(float, time_str.split('/'))
            return num / den
        except: return 0.0
    return float(time_str)

def format_srt_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    msecs = int(round((seconds - int(seconds)) * 1000))
    if msecs == 1000:
        msecs = 0
        secs += 1
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{msecs:03d}"

def process_xml_to_srt(xml_data):
    try:
        root = ET.fromstring(xml_data)
        titles = root.findall(".//title")
        srt_lines = []
        
        for i, title in enumerate(titles, 1):
            text_nodes = [node.text for node in title.iter() if node.text and not node.text.isspace()]
            content = " ".join(text_nodes).strip()
            if not content: continue
            
            offset = parse_fcp_time(title.get('offset', '0s'))
            duration = parse_fcp_time(title.get('duration', '0s'))
            start_time = offset
            end_time = offset + duration

            srt_lines.append(f"{i}")
            srt_lines.append(f"{format_srt_time(start_time)} --> {format_srt_time(end_time)}")
            srt_lines.append(f"{content}\n")
            
        return "\n".join(srt_lines)
    except Exception as e:
        return f"Error: {e}"

# --- UI Layout / 웹 화면 구성 ---
st.set_page_config(
    page_title="FREE FCPXML to SRT Converter | Final Cut Pro titles to captions | 파이널컷 타이틀 자막 변환 ", 
    page_icon="🎬",
    initial_sidebar_state="collapsed"
)

# --- 구글 서치 콘솔 인증 (헤더 삽입 시도) ---
st.markdown(
    '<meta name="google-site-verification" content="srl8-5iBlZ8PF8PXGw2VfxbSv-BVmdD0PoW0Ho8KUug" />', 
    unsafe_allow_html=True
)

# 제목 및 설명
st.title("🎬 FCPXML to SRT Converter")
st.subheader("Final Cut Pro XML 자막 변환기")

st.markdown("""
**[English]**
1. Export your project as **.fcpxml** from Final Cut Pro.
2. Upload the file below.
3. Download your **.srt** subtitle file.

**[한국어]**
1. 파이널컷 프로에서 프로젝트를 **.fcpxml**로 내보내세요.
2. 아래에 파일을 업로드하세요.
3. 변환된 **.srt** 자막 파일을 다운로드하세요.
""")

# 파일 업로드
uploaded_file = st.file_uploader("Choose a .fcpxml file / XML 파일을 선택하세요", type=['fcpxml', 'xml'])

if uploaded_file is not None:
    xml_binary = uploaded_file.read()
    srt_output = process_xml_to_srt(xml_binary)
    
    if srt_output.startswith("Error"):
        st.error(f"❌ Conversion Failed / 변환 실패: {srt_output}")
    else:
        st.success("✅ Conversion Success! / 변환 성공!")
        st.download_button(
            label="📥 Download SRT / 자막 다운로드",
            data=srt_output,
            file_name=f"{uploaded_file.name.split('.')[0]}.srt",
            mime="text/plain"
        )

# --- Donation Section / 후원 섹션 ---
st.markdown("---")
st.write("☕ **Support this project / 제작자 후원하기**")
st.write("If this tool saved your time, consider buying me a coffee! / 영상 편집 시간이 단축되었다면 커피 한 잔 사주세요!")

bmc_link = "https://www.buymeacoffee.com/jeong27" 
st.markdown(f'''
    <a href="{bmc_link}" target="_blank">
        <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 50px !important;width: 181px !important;" >
    </a>
''', unsafe_allow_html=True)

# --- FAQ Section 한영 병기 ---
st.markdown("---")
st.markdown("""
### Frequently Asked Questions (FAQ) / 자주 묻는 질문

**Q: How to convert FCPXML to SRT?**
* **A:** Simply export your Final Cut Pro project as an .fcpxml file and upload it to this tool. It will instantly convert your titles into a standard .srt subtitle file.
* **A(한글):** 파이널컷 프로에서 프로젝트를 .fcpxml로 내보낸 후 이 툴에 업로드하세요. 타이틀 자막을 즉시 표준 .srt 파일로 변환해 줍니다.

**Q: Is this FCPXML converter free?**
* **A:** Yes, this tool is completely free to use for all editors.
* **A(한글):** 네, 이 도구는 모든 편집자들을 위해 완전히 무료로 제공됩니다.

**Q: My XML file is not working.**
* **A:** Make sure you are using standard 'Title' clips in Final Cut Pro. If it still fails, please check the XML version.
* **A(한글):** 파이널컷 프로의 기본 '타이틀(Title)' 클립을 사용했는지 확인해 주세요. 계속 실패한다면 XML 버전 호환성을 확인해야 합니다.
""")
