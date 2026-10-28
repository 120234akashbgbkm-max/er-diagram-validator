// Change this ID if you prefer another video: the part after "watch?v=" in a YouTube link.
const VIDEO_ID = "QpdhBUYk7Kk";

export default function Learn() {
  return (
    <div className="page">
      <h1 className="page-title">Learn: ER Diagrams</h1>
      <p className="subtitle">Everything you need to read, draw and check an Entity-Relationship diagram.</p>

      {/* ---------------- 1. Concept explanation ---------------- */}
      <section className="card prose">
        <h2>1. Concept Explanation</h2>

        <h3>What is an ER diagram?</h3>
        <p>
          An Entity-Relationship (ER) diagram is a picture of a database design. It shows the <b>things</b> a system
          stores information about (entities), the <b>facts</b> stored about them (attributes), and how the things are{" "}
          <b>connected</b> (relationships). It is drawn before any tables are created, so mistakes are cheap to fix.
          The model was introduced by Peter Chen in 1976.
        </p>

        <h3>Building blocks</h3>
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Concept</th>
                <th>Meaning</th>
                <th>Chen notation</th>
                <th>Table notation (used by this tool)</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>Entity</td><td>A thing we store data about (Student, Order)</td><td>Rectangle</td><td>A table box with a title</td></tr>
              <tr><td>Attribute</td><td>A property of an entity (Name, Email)</td><td>Ellipse</td><td>A column row inside the table</td></tr>
              <tr><td>Primary key</td><td>Attribute(s) that uniquely identify each row</td><td>Underlined</td><td>Marked <code>PK</code></td></tr>
              <tr><td>Foreign key</td><td>Attribute that points to another table's key</td><td>Implied by the relationship</td><td>Marked <code>FK</code></td></tr>
              <tr><td>Relationship</td><td>How two entities are associated (Customer places Order)</td><td>Diamond</td><td>A line between tables</td></tr>
              <tr><td>Weak entity</td><td>Cannot be identified without its owner (Dependent of Employee)</td><td>Double rectangle</td><td>Key includes the owner's key</td></tr>
            </tbody>
          </table>
        </div>

        <h3>Types of attributes</h3>
        <ul>
          <li><b>Simple</b>: cannot be split (Age).</li>
          <li><b>Composite</b>: made of parts (Address = street + city + PIN).</li>
          <li><b>Multivalued</b>: several values per entity (phone numbers). It becomes its own table.</li>
          <li><b>Derived</b>: computed from others (Age from date of birth). Usually not stored.</li>
        </ul>

        <h3>Cardinality and participation</h3>
        <p>
          <b>Cardinality</b> says how many rows on one side relate to rows on the other: <b>1:1</b>, <b>1:N</b> or{" "}
          <b>M:N</b>. <b>Participation</b> says whether taking part is compulsory (<i>total</i>) or optional (
          <i>partial</i>). In crow's foot notation the line ends carry the symbols: a bar means one, a circle means zero
          and a three-pronged fork means many.
        </p>
        <pre className="code">{`Customer  1 ────< places >──── 0..N  Orders
Orders    1 ────< contains >─── 1..N  OrderItem
Student   M ────< enrols  >──── N     Course   (needs a junction table)`}</pre>

        <h3>Turning an ER diagram into tables</h3>
        <ol>
          <li>Every strong entity becomes a table; its key attribute becomes the primary key.</li>
          <li>For a 1:N relationship, put the key of the "1" side into the "N" table as a foreign key.</li>
          <li>For an M:N relationship, create a junction table that holds both keys.</li>
          <li>A multivalued attribute becomes a separate table with the owner's key.</li>
          <li>A weak entity's table uses the owner's key plus its own partial key.</li>
        </ol>

        <h3>Common design errors (what this tool checks)</h3>
        <ul>
          <li>A table with no primary key, or with no columns at all.</li>
          <li>Duplicate table or column names.</li>
          <li>A foreign key that does not point to any table, or a many-side table missing its foreign key.</li>
          <li>A relationship line attached to a single column instead of a table.</li>
          <li>Missing cardinality markers, or an unresolved many-to-many relationship.</li>
          <li>A table connected to nothing.</li>
          <li>
            Design smells found by the AI: derived values stored as columns, repeating groups (1NF), vague names, and
            normalization problems.
          </li>
        </ul>

        <h3>How this validator works</h3>
        <pre className="code">{`.drawio / image / PDF / .sql → FastAPI → parser (or AI reader for pictures) → tables, columns, relationships
              → rule-based checks (fast, always the same answer)
              → AI review (judgement calls the rules cannot make)
              → results + downloadable report`}</pre>
        <p>
          Rules handle anything that can be decided exactly. The AI is used only for judgement: naming, redundancy and
          normalization.
        </p>
      </section>

      {/* ---------------- 2. Video ---------------- */}
      <section className="card">
        <h2>2. Animated Video</h2>
        <div className="video-frame">
          <iframe
            src={`https://www.youtube.com/embed/${VIDEO_ID}`}
            title="Entity Relationship Diagram tutorial"
            allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>
        <p className="muted small">
          Video not loading?{" "}
          <a href={`https://www.youtube.com/watch?v=${VIDEO_ID}`} target="_blank" rel="noreferrer">
            Open it on YouTube
          </a>
          .
        </p>
      </section>

      {/* ---------------- 3. References ---------------- */}
      <section className="card prose">
        <h2>3. References</h2>

        <h3>Books</h3>
        <ul>
          <li>A. Silberschatz, H. F. Korth and S. Sudarshan, <i>Database System Concepts</i>, McGraw-Hill.</li>
          <li>R. Elmasri and S. B. Navathe, <i>Fundamentals of Database Systems</i>, Pearson.</li>
          <li>R. Ramakrishnan and J. Gehrke, <i>Database Management Systems</i>, McGraw-Hill.</li>
        </ul>

        <h3>Research paper</h3>
        <ul>
          <li>
            P. P. Chen, "The Entity-Relationship Model: Toward a Unified View of Data", <i>ACM Transactions on Database
            Systems</i>, vol. 1, no. 1, pp. 9-36, 1976.
          </li>
        </ul>

        <h3>Websites</h3>
        <ul>
          <li>
            Wikipedia, Entity-relationship model:{" "}
            <a href="https://en.wikipedia.org/wiki/Entity%E2%80%93relationship_model" target="_blank" rel="noreferrer">
              en.wikipedia.org/wiki/Entity-relationship_model
            </a>
          </li>
          <li>
            Wikiversity, Database Management / E-R Diagrams:{" "}
            <a href="https://en.wikiversity.org/wiki/Database_Management/E-R_Diagrams" target="_blank" rel="noreferrer">
              en.wikiversity.org/wiki/Database_Management/E-R_Diagrams
            </a>
          </li>
          <li>
            diagrams.net (draw.io), the tool used to draw the input diagrams:{" "}
            <a href="https://www.drawio.com" target="_blank" rel="noreferrer">drawio.com</a>
          </li>
        </ul>

        <h3>Videos</h3>
        <ul>
          <li>
            "Entity Relationship Diagram (ERD) Tutorial - Part 1", YouTube (embedded above; listed on{" "}
            <a href="https://learnlearn.uk/alevelcs/entity-relationship-diagrams/" target="_blank" rel="noreferrer">
              learnlearn.uk
            </a>
            ).
          </li>
        </ul>

        <h3>Technologies used to build this project</h3>
        <ul>
          <li>React and Vite (frontend), FastAPI and Python (backend), Google Gemini API (AI review and quiz).</li>
        </ul>
      </section>
    </div>
  );
}
