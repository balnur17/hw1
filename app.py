import os
import json
from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
from flask import send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Папка для загрузок
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Создаём папку uploads, если её нет
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ADMIN_PASSWORD = "teacher123"

ANSWERS_FILE = "answers.json"
if not os.path.exists(ANSWERS_FILE):
    with open(ANSWERS_FILE, "w") as f:
        json.dump([], f)

def save_answer(data):
    with open(ANSWERS_FILE, "r") as f:
        answers = json.load(f)
    answers.append(data)
    with open(ANSWERS_FILE, "w") as f:
        json.dump(answers, f, indent=2)

def get_answers():
    with open(ANSWERS_FILE, "r") as f:
        return json.load(f)

# Студенческая страница (я сокращу HTML до минимума, чтобы проверить работу)
# Но вы можете оставить полную версию. Я оставлю полную, чтобы не потерять функционал.
# Однако для теста можно временно упростить. Оставлю ваш предыдущий HTML с тремя кнопками.

STUDENT_PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Techquest</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #0a0f1c; font-family: 'Inter', system-ui; color: #eef2ff; padding: 2rem 1.5rem; }
        .container { max-width: 1300px; margin: 0 auto; }
        .header h1 { font-size: 2.2rem; text-align: center; background: linear-gradient(135deg, #c084fc, #3b82f6); -webkit-background-clip: text; background-clip: text; color: transparent; margin-bottom: 1rem; }
        .student-info { background: #111827; border-radius: 2rem; padding: 0.8rem 1.5rem; margin-bottom: 2rem; display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 1rem; border: 1px solid #2d3a5e; }
        .student-info input { background: #0a0f1c; border: 1px solid #334155; border-radius: 2rem; padding: 0.5rem 1rem; color: white; width: 250px; }
        button { background: #2563eb; border: none; border-radius: 2rem; padding: 0.5rem 1.2rem; color: white; cursor: pointer; }
        .segments { display: flex; gap: 1.8rem; justify-content: center; margin-bottom: 2.5rem; flex-wrap: wrap; }
        .segment-card { background: #111827; border-radius: 1.8rem; padding: 1.5rem 2rem; width: 260px; text-align: center; cursor: pointer; border: 1px solid #2d3a5e; }
        .segment-card.active { border-color: #3b82f6; background: #1e293b; }
        .content-panel { background: #0f172ac9; border-radius: 2rem; padding: 1.8rem; display: none; border: 1px solid #2d3f5e; margin-top: 1rem; }
        .content-panel.active-panel { display: block; }
        .task-card { background: #0f172a; border-radius: 1.2rem; padding: 1.2rem; margin-bottom: 1.5rem; border: 1px solid #28344e; }
        textarea, input[type=text] { width: 100%; background: #0a0f1c; border: 1px solid #334155; border-radius: 1rem; padding: 0.7rem; color: white; margin: 0.5rem 0; }
        .record-controls { display: flex; gap: 1rem; justify-content: center; margin: 1rem 0; }
        .feedback { margin-top: 0.5rem; font-size: 0.85rem; }
        .random-app-name { font-size: 1.8rem; background: #2d3a5e; display: inline-block; padding: 0.2rem 1.2rem; border-radius: 3rem; margin: 0.8rem 0; color: #facc15; }
        .badge { font-size: 0.7rem; background: #1f3a5f; padding: 0.2rem 0.8rem; border-radius: 2rem; display: inline-block; }
        .submit-btn { background: #10b981; margin-top: 1rem; width: 100%; }
    </style>
</head>
<body>
<div class="container">
    <div class="header"><h1>Techquest</h1></div>
    <div class="student-info">
        <label><i class="fas fa-user-graduate"></i> Your name:</label>
        <input type="text" id="studentName" placeholder="e.g. Aidar Sapar">
    </div>
    <div class="segments">
        <div class="segment-card" data-panel="vocabPanel"><i class="fas fa-book-open"></i><h2>Vocabulary</h2></div>
        <div class="segment-card" data-panel="grammarPanel"><i class="fas fa-code"></i><h2>Grammar</h2></div>
        <div class="segment-card" data-panel="speakingPanel"><i class="fas fa-microphone-alt"></i><h2>Speaking</h2></div>
    </div>
    <!-- VOCABULARY PANEL -->
    <div id="vocabPanel" class="content-panel">
        <div class="task-card">
            <div id="vocabDefinition" style="background:#1e293b; padding:0.8rem; border-radius:1rem;">Loading...</div>
            <input type="text" id="vocabAnswer" placeholder="Your answer...">
            <button id="checkVocabBtn">Check</button>
            <button id="nextVocabBtn">Next word</button>
            <div id="vocabFeedback" class="feedback"></div>
            <button id="submitVocabBtn" class="submit-btn">📤 Submit Vocabulary to teacher</button>
        </div>
    </div>
    <!-- GRAMMAR PANEL -->
    <div id="grammarPanel" class="content-panel">
        <div class="task-card"><div>Task 1 (reported speech):<br>User said: "I can't find the app."</div>
        <textarea id="reported1" rows="2"></textarea><button class="grammar-check" data-task="rep1">Check</button><div id="fb1" class="feedback"></div></div>
        <div class="task-card"><div>Task 2 (question):<br>She asked: "Does this app work offline?"</div>
        <textarea id="reported2" rows="2"></textarea><button class="grammar-check" data-task="rep2">Check</button><div id="fb2" class="feedback"></div></div>
        <div class="task-card"><div>Task 3 (on behalf of / tech-savvy):<br>Русский: «Я открываю этот почтовый ящик от имени своей матери...»</div>
        <textarea id="behalfTask" rows="2"></textarea><button class="grammar-check" data-task="behalf">Check</button><div id="fb3" class="feedback"></div></div>
        <div class="task-card"><div>Task 4 (prepositions):<br>confined ___ , detract ___ , integrated ___</div>
        <input id="prep1" placeholder="1"><input id="prep2" placeholder="2"><input id="prep3" placeholder="3">
        <button class="grammar-check" data-task="preps">Check</button><div id="fb4" class="feedback"></div></div>
        <div class="task-card"><div>Task 5 (verb patterns):<br>I enjoy ___ , refused ___ , helped me ___</div>
        <textarea id="verbComp" rows="3"></textarea><button class="grammar-check" data-task="verb">Check</button><div id="fb5" class="feedback"></div></div>
        <button id="submitGrammarBtn" class="submit-btn">📤 Submit Grammar to teacher</button>
    </div>
    <!-- SPEAKING PANEL -->
    <div id="speakingPanel" class="content-panel">
        <div class="task-card">
            <p>Your random app: <span class="random-app-name" id="randomAppName"></span></p>
            <div class="record-controls">
                <button id="startRecordBtn">Start recording</button>
                <button id="stopRecordBtn" disabled>Stop</button>
                <button id="playRecordBtn" disabled>Play</button>
            </div>
            <audio id="audioPlayback" controls style="display:none;"></audio>
            <div id="speakingFeedback" class="feedback"></div>
            <button id="submitSpeakingBtn" class="submit-btn">📤 Submit Speaking to teacher</button>
        </div>
    </div>
</div>
<script>
    const vocabItems = [
        { word: "tech savvy", definition: "A person skilled in using digital technology." },
        { word: "digital native", definition: "Born during the age of digital technology." },
        { word: "algorithm", definition: "Set of rules for problem-solving." },
        { word: "spreadsheet", definition: "Electronic document with rows and columns." },
        { word: "adblocker", definition: "Software that blocks ads." },
        { word: "manufacturing", definition: "Large-scale production using machinery." },
        { word: "transactions", definition: "Business deals, buying/selling." },
        { word: "encrypted", definition: "Converted into code for security." },
        { word: "cloud library", definition: "Remote digital storage service." }
    ];
    let currentVocab = 0;
    const vocabDef = document.getElementById("vocabDefinition");
    const vocabAnswer = document.getElementById("vocabAnswer");
    const vocabFeedback = document.getElementById("vocabFeedback");
    function loadVocab() { vocabDef.innerText = vocabItems[currentVocab].definition; vocabAnswer.value = ""; vocabFeedback.innerHTML = ""; }
    document.getElementById("checkVocabBtn").onclick = () => {
        let ans = vocabAnswer.value.trim().toLowerCase();
        let correct = vocabItems[currentVocab].word.toLowerCase();
        if(ans===correct) vocabFeedback.innerHTML="✓ Correct";
        else vocabFeedback.innerHTML=`✗ Correct answer: ${vocabItems[currentVocab].word}`;
    };
    document.getElementById("nextVocabBtn").onclick = () => { currentVocab = (currentVocab+1)%vocabItems.length; loadVocab(); };
    loadVocab();

    document.querySelectorAll(".grammar-check").forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.target.nextElementSibling.innerHTML = "✓ Checked (will be saved on submit)";
        });
    });

    let mediaRecorder, audioChunks, audioBlob = null;
    const startBtn = document.getElementById("startRecordBtn");
    const stopBtn = document.getElementById("stopRecordBtn");
    const playBtn = document.getElementById("playRecordBtn");
    const audioPlay = document.getElementById("audioPlayback");
    const speakFeedback = document.getElementById("speakingFeedback");
    startBtn.onclick = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
            mediaRecorder.onstop = () => {
                audioBlob = new Blob(audioChunks, { type: "audio/webm" });
                const url = URL.createObjectURL(audioBlob);
                audioPlay.src = url;
                audioPlay.style.display = "block";
                playBtn.disabled = false;
                speakFeedback.innerHTML = "Recording ready.";
                stream.getTracks().forEach(t=>t.stop());
            };
            mediaRecorder.start();
            startBtn.disabled = true;
            stopBtn.disabled = false;
            playBtn.disabled = true;
            speakFeedback.innerHTML = "🔴 Recording...";
        } catch(e) {
            speakFeedback.innerHTML = "❌ Microphone access needed.";
        }
    };
    stopBtn.onclick = () => { if(mediaRecorder && mediaRecorder.state !== "inactive") { mediaRecorder.stop(); startBtn.disabled = false; stopBtn.disabled = true; } };
    playBtn.onclick = () => { if(audioPlay.src) audioPlay.play(); };
    const apps = ["Kaspi.kz","Wildberries","Yandex Go","Halyk Bank","2GIS","Telegram","Zoom"];
    document.getElementById("randomAppName").innerText = apps[Math.floor(Math.random()*apps.length)];

    const studentNameInput = document.getElementById("studentName");
    async function sendData(segment, formData) {
        const name = studentNameInput.value.trim();
        if(!name) { alert("Enter your name first"); return false; }
        formData.append("student_name", name);
        formData.append("segment", segment);
        const response = await fetch("/submit", { method: "POST", body: formData });
        if(response.ok) {
            alert(`${segment} answers submitted successfully!`);
            return true;
        } else {
            alert("Error submitting. Try again.");
            return false;
        }
    }
    document.getElementById("submitVocabBtn").onclick = async () => {
        const formData = new FormData();
        formData.append("vocab_word", vocabItems[currentVocab].word);
        formData.append("vocab_answer", vocabAnswer.value.trim());
        await sendData("vocabulary", formData);
    };
    document.getElementById("submitGrammarBtn").onclick = async () => {
        const formData = new FormData();
        formData.append("reported1", document.getElementById("reported1").value);
        formData.append("reported2", document.getElementById("reported2").value);
        formData.append("behalf", document.getElementById("behalfTask").value);
        formData.append("prep1", document.getElementById("prep1").value);
        formData.append("prep2", document.getElementById("prep2").value);
        formData.append("prep3", document.getElementById("prep3").value);
        formData.append("verbComp", document.getElementById("verbComp").value);
        await sendData("grammar", formData);
    };
    document.getElementById("submitSpeakingBtn").onclick = async () => {
        if(!audioBlob) { alert("Please record your voice first."); return; }
        const formData = new FormData();
        formData.append("speaking_app", document.getElementById("randomAppName").innerText);
        formData.append("audio", audioBlob, `${studentNameInput.value.trim()}_speaking.webm`);
        await sendData("speaking", formData);
    };
    const panels = {
        vocabPanel: document.getElementById("vocabPanel"),
        grammarPanel: document.getElementById("grammarPanel"),
        speakingPanel: document.getElementById("speakingPanel")
    };
    document.querySelectorAll(".segment-card").forEach(card => {
        card.addEventListener("click", () => {
            Object.keys(panels).forEach(pid => panels[pid].classList.remove("active-panel"));
            panels[card.dataset.panel].classList.add("active-panel");
            document.querySelectorAll(".segment-card").forEach(c => c.classList.remove("active"));
            card.classList.add("active");
        });
    });
    document.querySelector(".segment-card[data-panel='vocabPanel']").click();
</script>
</body>
</html>"""

ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Techquest Admin</title>
    <style>
        body { font-family: system-ui; background: #0a0f1c; color: #eee; padding: 2rem; }
        table { border-collapse: collapse; width: 100%; background: #111827; border-radius: 1rem; overflow: auto; display: block; }
        th, td { border: 1px solid #2d3a5e; padding: 0.8rem; text-align: left; vertical-align: top; }
        th { background: #1e293b; }
        audio { max-width: 200px; }
        .segment-badge { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 1rem; font-size: 0.7rem; font-weight: bold; }
        .segment-vocab { background: #3b82f6; }
        .segment-grammar { background: #8b5cf6; }
        .segment-speaking { background: #10b981; }
    </style>
</head>
<body>
    <h1>📋 Student Answers</h1>
    <p><a href="/admin/logout">Logout</a></p>
    <div style="overflow-x: auto;">
    <table>
        <tr>
            <th>Time</th>
            <th>Student</th>
            <th>Segment</th>
            <th>Details</th>
            <th>Audio</th>
        </tr>
        {% for a in answers %}
        <tr>
            <td>{{ a.timestamp[:19] }}</td>
            <td>{{ a.student_name }}</td>
            <td><span class="segment-badge segment-{{ a.segment }}">{{ a.segment }}</span></td>
            <td>
                {% if a.segment == 'vocabulary' %}
                    <strong>Word:</strong> {{ a.vocab_word }}<br>
                    <strong>Answer:</strong> {{ a.vocab_answer }}
                {% elif a.segment == 'grammar' %}
                    <strong>Reported1:</strong> {{ a.reported1 }}<br>
                    <strong>Reported2:</strong> {{ a.reported2 }}<br>
                    <strong>OnBehalf:</strong> {{ a.behalf }}<br>
                    <strong>Prepositions:</strong> {{ a.prep1 }} / {{ a.prep2 }} / {{ a.prep3 }}<br>
                    <strong>Verb patterns:</strong> {{ a.verbComp }}
                {% elif a.segment == 'speaking' %}
                    <strong>App:</strong> {{ a.speaking_app }}
                {% endif %}
            </td>
            <td>
                {% if a.audio_file %}
                    <a href="/uploads/{{ a.audio_file }}" target="_blank">Play/Download</a>
                {% else %}—{% endif %}
            </td>
        </tr>
        {% endfor %}
    </table>
    </div>
</body>
</html>"""

@app.route("/")
def student():
    return render_template_string(STUDENT_PAGE)

@app.route("/submit", methods=["POST"])
def submit():
    segment = request.form.get("segment", "unknown")
    data = {
        "timestamp": datetime.now().isoformat(),
        "student_name": request.form.get("student_name", ""),
        "segment": segment,
        "audio_file": None
    }
    if segment == "vocabulary":
        data["vocab_word"] = request.form.get("vocab_word", "")
        data["vocab_answer"] = request.form.get("vocab_answer", "")
    elif segment == "grammar":
        data["reported1"] = request.form.get("reported1", "")
        data["reported2"] = request.form.get("reported2", "")
        data["behalf"] = request.form.get("behalf", "")
        data["prep1"] = request.form.get("prep1", "")
        data["prep2"] = request.form.get("prep2", "")
        data["prep3"] = request.form.get("prep3", "")
        data["verbComp"] = request.form.get("verbComp", "")
    elif segment == "speaking":
        data["speaking_app"] = request.form.get("speaking_app", "")
        if "audio" in request.files:
            file = request.files["audio"]
            if file.filename:
                filename = secure_filename(f"{data['student_name']}_{datetime.now().timestamp()}.webm")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                data["audio_file"] = filename
    save_answer(data)
    return jsonify({"status": "ok"}), 200

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return "Wrong password", 403
    if session.get("admin"):
        return redirect(url_for("admin_dashboard"))
    return '''
        <form method="post">
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    '''

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin"))
    answers = get_answers()
    return render_template_string(ADMIN_TEMPLATE, answers=answers[::-1])

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin"))

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    if not session.get("admin"):
        return "Unauthorized", 401
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)