"""
AI Clipboard ++ - Streamlit Web Application
あなたの「メモ書き」を、プロ級の「成果物」へ。
"""

import streamlit as st
import os

# --- ページ設定 ---
st.set_page_config(
    page_title="AI Clipboard ++",
    page_icon="📋",
    layout="centered"
)

# --- UIデザイン ---
st.title("📋 AI Clipboard ++")
st.caption("あなたの「メモ書き」を、プロ級の「成果物」へ。")

# --- サイドバー: 設定 ---
st.sidebar.header("⚙️ 設定")
api_key = st.sidebar.text_input("Gemini API Key", type="password")

# APIキーの設定状態を確認
model = None
if api_key:
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        st.sidebar.success("✅ API接続成功")
    except Exception as e:
        st.sidebar.error(f"❌ API接続エラー: {e}")
else:
    st.sidebar.warning("⚠️ APIキーを入力してください")
    st.info("""
    ### 使い方
    1. 左のサイドバーにGemini APIキーを入力
    2. 下のテキストエリアにラフなメモを入力
    3. 変換スタイルを選択
    4. 「変換・最適化する」ボタンをクリック
    
    APIキーは [Google AI Studio](https://aistudio.google.com/) で無料取得できます。
    """)


# --- ロジッククラス ---
class DataSynthesizer:
    """Few-Shotデータ合成"""
    def __init__(self, model):
        self.model = model
        
    def generate_examples(self, intent: str, count: int = 3) -> str:
        prompt = f"""ユーザーの意図「{intent}」を達成するための、理想的な「入力と出力の例」を{count}つ作成せよ。
Example 1:
Input: ...
Output: ..."""
        try:
            return self.model.generate_content(prompt).text.strip()
        except:
            return ""


class CasualTextRefiner:
    """テキスト最適化"""
    def __init__(self, model):
        self.model = model
        self.synthesizer = DataSynthesizer(model)
    
    def refine(self, user_text: str, style: str, use_few_shot: bool):
        with st.status("🧠 AIが思考中...", expanded=True) as status:
            # 1. 意図理解
            st.write("1. あなたの意図を分析しています...")
            intent_resp = self.model.generate_content(
                f"以下のテキストの目的を簡潔に要約せよ: {user_text}"
            )
            intent = intent_resp.text.strip()
            st.write(f"👉 意図: **{intent}**")
            
            # 2. Few-Shotデータ合成
            examples = ""
            if use_few_shot:
                st.write("2. 成功事例（Few-Shotデータ）を合成しています...")
                examples = self.synthesizer.generate_examples(intent)
                with st.expander("🔍 生成された学習データを見る"):
                    st.text(examples)
            
            # 3. 変換実行
            st.write("3. 最適化を実行中...")
            prompt = f"""
以下の「ラフな入力」を「スタイル」に合わせて書き直せ。
{'【参考事例】' + examples if examples else ''}
【スタイル】{style}
【入力】{user_text}
出力は書き直した結果のみ。"""
            
            response = self.model.generate_content(prompt)
            status.update(label="✅ 完了！", state="complete", expanded=False)
            return response.text.strip()


# --- メイン画面 ---
st.divider()

# 1. 入力エリア
user_input = st.text_area(
    "📝 ラフなメモを入力 (話し言葉でOK)",
    height=150,
    placeholder="例: 部長にお詫び。寝坊して会議遅刻した。明日の資料は必ず今日中に送るって伝えて。"
)

# 2. 設定エリア
col1, col2 = st.columns(2)
with col1:
    target_style = st.selectbox(
        "🎨 変換スタイル",
        [
            "ビジネスメール (謝罪・依頼)",
            "エンジニア向け (要件定義)",
            "SNS投稿 (親しみやすく)",
            "英語翻訳 (ビジネス)",
            "論理的要約 (箇条書き)",
            "丁寧なカスタマーサポート",
            "技術ドキュメント"
        ]
    )
with col2:
    use_few_shot = st.checkbox(
        "🧬 Data Synthesis を使う",
        value=True,
        help="ONにすると、AIが「良い例」を生成してから学習し、精度を高めます。"
    )

# 3. 実行ボタン
st.divider()
if st.button("✨ 変換・最適化する", type="primary", use_container_width=True):
    if not api_key:
        st.error("⚠️ サイドバーからAPIキーを入力してください")
    elif not user_input:
        st.error("⚠️ テキストを入力してください")
    else:
        try:
            refiner = CasualTextRefiner(model)
            result = refiner.refine(user_input, target_style, use_few_shot)
            
            st.subheader("📄 出力結果")
            st.text_area("コピー用", value=result, height=250)
            st.success("✅ コピーしてご利用ください！")
        except Exception as e:
            st.error(f"❌ エラー: {e}")

# --- フッター ---
st.divider()
st.caption("Powered by Prompt Engineering Library & Google Gemini")
