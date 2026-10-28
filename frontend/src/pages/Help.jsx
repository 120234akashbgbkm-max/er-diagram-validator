export default function Help() {
  return (
    <div className="page">
      <h1 className="page-title">Help: User Manual</h1>
      <p className="subtitle">How to use the AI-Based ER Diagram Validator, step by step.</p>

      <section className="card prose">
        <h2>What this website does</h2>
        <p>
          You upload an ER diagram drawn in draw.io. The website reads the tables, columns and relationships in it,
          checks the design for mistakes, and shows you exactly what is wrong and how to fix it. An AI reviewer then
          adds higher-level feedback, and you can download a full report.
        </p>
      </section>

      <section className="card prose">
        <h2>Which files can I upload?</h2>
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr><th>File</th><th>How it is read</th><th>Accuracy</th></tr>
            </thead>
            <tbody>
              <tr><td><b>.drawio</b> (table shapes)</td><td>Read directly from the file</td><td>Exact</td></tr>
              <tr><td><b>.sql</b> or text containing CREATE TABLE</td><td>Read directly from the SQL</td><td>Exact</td></tr>
              <tr><td><b>.drawio</b> (Chen ovals and diamonds)</td><td>Interpreted by AI</td><td>Check the Table Summary</td></tr>
              <tr><td><b>Image</b> (PNG, JPG, WebP, GIF, BMP, HEIC) or <b>PDF</b></td><td>The AI reads the picture</td><td>Check the Table Summary</td></tr>
              <tr><td><b>Word</b> (.docx), Excel, PowerPoint</td><td>The AI reads the text and pictures inside</td><td>Check the Table Summary</td></tr>
              <tr><td><b>Text</b> (Mermaid, PlantUML, JSON, XML, .txt)</td><td>Interpreted by AI</td><td>Check the Table Summary</td></tr>
            </tbody>
          </table>
        </div>
        <p>
          The file type is detected from the file's content, not just its name. Maximum size is 15 MB. When the AI reads a picture, a yellow notice appears. Compare the Table Summary with
          your diagram before trusting the results, because AI can occasionally misread small text. The AI is told to
          copy what is drawn and never to add keys or fix mistakes, so errors in your diagram are still reported.
        </p>
      </section>

      <section className="card prose">
        <h2>Before you start: drawing your diagram in draw.io</h2>
        <ol>
          <li>Open <b>draw.io</b> (diagrams.net) and draw your diagram using the <b>Entity Relation</b> shapes.</li>
          <li>Each table is a box with its name as the title. Each column is a row inside the box.</li>
          <li>Write each column as <code>PK  order_id : INT</code>. Use <code>PK</code> for a primary key and{" "}
            <code>FK</code> for a foreign key. The <code>: TYPE</code> part is the data type.</li>
          <li>Connect tables with lines and set the ER arrow ends (for example "One" and "Zero or many").</li>
          <li>Save with <b>File → Save as</b> and keep the <code>.drawio</code> extension.</li>
        </ol>
      </section>

      <section className="card prose">
        <h2>Using the Validator (Home page)</h2>
        <ol>
          <li><b>Choose the file.</b> Click the file box and pick your diagram: a <code>.drawio</code> file, an image, a PDF, a Word document, or a <code>.sql</code> file.</li>
          <li><b>Click "Validate Diagram".</b> The file is sent to the server, parsed, and checked by the rules.</li>
          <li><b>Read the result.</b> You will see the counts of errors and warnings, the list of problems, and a Table Summary.</li>
          <li><b>Click "Run AI Review"</b> (optional) for extra feedback on naming, redundancy and normalization. It takes a few seconds.</li>
          <li><b>Download the report</b> as PDF, Word or Text using the buttons at the bottom of the results.</li>
        </ol>
      </section>

      <section className="card prose">
        <h2>Understanding the output</h2>
        <div className="table-wrap">
          <table className="data-table">
            <tbody>
              <tr><td className="text-error strong">❌ Error</td><td>A real design problem, such as a table with no primary key. Fix these first.</td></tr>
              <tr><td className="text-warn strong">⚠️ Warning</td><td>Something suspicious, such as a missing cardinality marker. Check it and decide.</td></tr>
              <tr><td className="strong">💡 Suggestion</td><td>Shown under AI findings. It tells you how to fix the problem.</td></tr>
              <tr><td className="strong">Table Summary</td><td>One row per table: number of columns, primary key, foreign keys and relationships. Red rows have errors, amber rows have warnings.</td></tr>
              <tr><td className="strong">PK / FK badges</td><td>Mark primary-key and foreign-key columns in the table cards.</td></tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="card prose">
        <h2>What each button does</h2>
        <div className="table-wrap">
          <table className="data-table">
            <tbody>
              <tr><td className="strong">Validate Diagram</td><td>Parses the file and runs the rule-based checks.</td></tr>
              <tr><td className="strong">Run AI Review</td><td>Sends the parsed diagram to the AI for semantic feedback.</td></tr>
              <tr><td className="strong">Download PDF / Word / Text</td><td>Saves a report with your input, the processing steps, the parsed tables and the final results.</td></tr>
              <tr><td className="strong">QUIZ</td><td>Starts an AI-generated quiz. Choose how many questions and the difficulty.</td></tr>
              <tr><td className="strong">COMPETITIVE EXAM</td><td>Opens 50+ solved practice questions with answers and step-by-step solutions.</td></tr>
              <tr><td className="strong">Learn</td><td>Concept explanation, an explainer video and references.</td></tr>
              <tr><td className="strong">Developed By</td><td>The team and the faculty guide.</td></tr>
              <tr><td className="strong">☀ / 🌙</td><td>Switches between Day mode and Night mode.</td></tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="card prose">
        <h2>How the processing works</h2>
        <ol>
          <li>The browser sends your file to the FastAPI server.</li>
          <li>The server reads the draw.io XML and extracts tables, columns, keys and relationships.</li>
          <li>Rule-based checks run: keys, foreign keys, cardinality, connections, duplicates, isolated tables.</li>
          <li>If you ask for it, the AI reviews the parsed design for problems that rules cannot judge.</li>
        </ol>
      </section>

      <section className="card prose">
        <h2>Using the Quiz</h2>
        <ol>
          <li>Click <b>QUIZ</b> in the top bar.</li>
          <li>Enter the number of questions and choose Easy, Medium or Hard, then click <b>Start Quiz</b>.</li>
          <li>Pick an option and click <b>Submit Answer</b>. You will see whether you were right, plus an explanation.</li>
          <li>Click <b>Next Question</b> until the end. You then get your score and a summary.</li>
        </ol>
      </section>

      <section className="card prose">
        <h2>Troubleshooting</h2>
        <ul>
          <li><b>"Failed to fetch":</b> the backend server is not running. Start it and try again.</li>
          <li><b>"No ER diagram could be found":</b> the AI did not see a diagram in the file. Try a clearer or larger image.</li>
          <li><b>"The AI could not read this file" (503):</b> the AI is busy. Wait a minute and try again.</li>
          <li><b>"The file is too large":</b> files must be under 15 MB.</li>
          <li><b>AI review fails with 503:</b> the AI service is busy. Wait a minute and click again.</li>
          <li><b>The quiz says it used the built-in question bank:</b> the AI was unavailable, so stored questions were used.</li>
        </ul>
      </section>
    </div>
  );
}
