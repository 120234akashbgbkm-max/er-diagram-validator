"""
question_bank.py
Solved practice questions for the Competitive Exam page (and the quiz fallback).

These are ORIGINAL practice questions written in the style of GATE / PSU database
papers. They are not copied from past papers, so they carry a "practice" tag and
no exam year. If you later verify a question against an official paper, change its
tag to e.g. "GATE 2014".
"""

_TAG = "GATE-style practice"
_RAW = []


def _q(difficulty, topic, question, options, answer, explanation, tag=_TAG):
    _RAW.append(dict(difficulty=difficulty, topic=topic, question=question,
                     options=options, answer=answer, explanation=explanation, tag=tag))


# ---------------- ER model basics ----------------
_q("Easy", "ER basics", "In Chen notation, which shape represents an entity set?",
   ["Diamond", "Rectangle", "Ellipse", "Triangle"], 1,
   "Step 1: Recall the Chen symbols. Rectangle = entity set, ellipse = attribute, diamond = relationship set.\nStep 2: The question asks for the entity set, so the answer is Rectangle.")
_q("Easy", "ER basics", "Which symbol represents a multivalued attribute in Chen notation?",
   ["Dashed ellipse", "Double ellipse", "Underlined ellipse", "Double rectangle"], 1,
   "A multivalued attribute (e.g. phone numbers) is drawn as a double ellipse. A dashed ellipse is a derived attribute, an underlined label marks a key attribute, and a double rectangle is a weak entity.")
_q("Easy", "ER basics", "A dashed ellipse in an ER diagram denotes a:",
   ["Key attribute", "Multivalued attribute", "Derived attribute", "Composite attribute"], 2,
   "A derived attribute can be computed from other attributes (e.g. Age from Date of Birth), and is drawn with a dashed ellipse.")
_q("Easy", "ER basics", "A weak entity set is drawn as a:",
   ["Double rectangle", "Double diamond", "Dashed rectangle", "Rounded rectangle"], 0,
   "A weak entity set has no key of its own and is drawn as a double rectangle. Its identifying relationship is drawn as a double diamond.")
_q("Easy", "ER basics", "Which attribute is shown with an underlined name in an ER diagram?",
   ["Derived attribute", "Multivalued attribute", "Key attribute", "Composite attribute"], 2,
   "The underline marks the attribute (or attributes) that uniquely identify each entity: the key attribute.")
_q("Easy", "ER basics", "Which of the following is a composite attribute?",
   ["Roll number", "Address made of street, city and PIN code", "Gender", "Salary"], 1,
   "A composite attribute can be divided into smaller meaningful parts. Address splits into street, city and PIN code; the others are simple attributes.")
_q("Easy", "ER basics", "The degree of a relationship set is:",
   ["The number of attributes it has", "The number of entity sets participating in it", "The number of tuples it holds", "The number of keys it has"], 1,
   "Degree = number of participating entity sets. Binary = 2, ternary = 3.")
_q("Easy", "ER basics", "A relationship among Doctor, Patient and Medicine is called a:",
   ["Unary relationship", "Binary relationship", "Ternary relationship", "Recursive relationship"], 2,
   "Three entity sets participate, so the degree is 3: a ternary relationship.")
_q("Easy", "ER basics", "Total participation is shown in an ER diagram using:",
   ["A dashed line", "A double line", "A thick arrow", "A zigzag line"], 1,
   "Total participation (every entity must take part) uses a double line from the entity to the relationship. Partial participation uses a single line.")
_q("Easy", "ER basics", "Which of the following is NOT a type of attribute in the ER model?",
   ["Simple", "Composite", "Multivalued", "Recursive"], 3,
   "Simple, composite, multivalued, derived and key attributes exist. 'Recursive' describes a relationship, not an attribute.")
_q("Easy", "ER basics", "'Employee supervises Employee' is an example of a:",
   ["Ternary relationship", "Recursive (unary) relationship", "Weak relationship", "Identifying relationship"], 1,
   "The same entity set takes part twice in the relationship (in different roles: supervisor and subordinate). This is a recursive or unary relationship.")
_q("Easy", "ER basics", "'Every employee must belong to some department' expresses:",
   ["Partial participation of Employee", "Total participation of Employee", "A key constraint", "A weak entity"], 1,
   "'Every' entity must participate in the relationship, which is total participation.")
_q("Easy", "ER basics", "Which notation shows cardinality using symbols at the line ends, such as a 'crow's foot'?",
   ["Chen notation only", "Crow's foot (Information Engineering) notation", "UML sequence diagrams", "Data flow diagrams"], 1,
   "Crow's foot notation puts cardinality symbols (bars, circles, three-pronged forks) at the ends of the relationship line.")
_q("Medium", "ER basics", "In crow's foot notation, the symbol for 'zero or many' is:",
   ["A single bar", "A circle together with a three-pronged fork", "Two bars", "A double line"], 1,
   "The circle means 'zero' (optional) and the three-pronged fork means 'many', so together they mean zero or many.")
_q("Medium", "ER basics", "Aggregation in ER modeling is used when:",
   ["An attribute is multivalued", "A relationship must itself take part in another relationship", "An entity has no key", "Two attributes are equal"], 1,
   "Relationships normally relate entities. When a whole relationship needs to relate to another entity, we treat it as an abstract entity (aggregation).")

# ---------------- Cardinality, participation, weak entities ----------------
_q("Easy", "Cardinality", "Many employees work in one department. The cardinality ratio from Employee to Department is:",
   ["1:1", "1:N", "N:1", "M:N"], 2,
   "Each employee has one department, and each department has many employees. Read from Employee to Department, that is N:1.")
_q("Easy", "Cardinality", "A student can enrol in many courses and a course can have many students. The cardinality is:",
   ["1:1", "1:N", "N:1", "M:N"], 3,
   "Many on both sides gives M:N.")
_q("Easy", "Weak entities", "The primary key of the relation for a weak entity set is formed from:",
   ["Its discriminator alone", "The owner's primary key alone", "The owner's primary key plus its own discriminator (partial key)", "Any foreign key"], 2,
   "A weak entity cannot be identified on its own. Its table's key is the owner's primary key combined with the partial key (discriminator).")
_q("Easy", "Weak entities", "An identifying relationship connects:",
   ["Two strong entity sets", "A weak entity set to its owner entity set", "Two weak entity sets with no owner", "An attribute to an entity"], 1,
   "The identifying relationship (double diamond) links a weak entity to the owner entity that supplies part of its key.")
_q("Easy", "Weak entities", "A weak entity set and its owner entity set normally have which relationship?",
   ["M:N", "One-to-many from owner to weak entity", "Many-to-one from owner to weak entity", "Ternary"], 1,
   "One owner can have many dependent weak entities (for example one Employee, many Dependents), but each weak entity has exactly one owner.")

# ---------------- ER to relational mapping ----------------
_q("Medium", "ER to relational", "Entity sets A and B (simple attributes only) are in an M:N relationship R. The minimum number of relations needed is:",
   ["1", "2", "3", "4"], 2,
   "Step 1: A needs a table. Step 2: B needs a table.\nStep 3: An M:N relationship needs its own table holding the keys of A and B.\nTotal = 3.")
_q("Medium", "ER to relational", "A 1:N relationship R relates A (the 1 side) and B (the N side), and B participates totally. The minimum number of relations is:",
   ["1", "2", "3", "4"], 1,
   "Put the key of A into B's table as a foreign key, so R needs no table of its own. Tables: A and B = 2. They cannot be merged because one A row is shared by many B rows.")
_q("Medium", "ER to relational", "A 1:1 relationship R between A and B with total participation on both sides can be mapped using a minimum of how many relations?",
   ["1", "2", "3", "4"], 0,
   "Total participation on both sides of a 1:1 relationship means every A row pairs with exactly one B row and vice versa, so everything can be merged into a single relation.")
_q("Medium", "ER to relational", "How is a multivalued attribute of an entity mapped to the relational model?",
   ["As an extra column in the entity's table", "As a separate relation holding the entity's key and the attribute", "As a foreign key only", "It is ignored"], 1,
   "A column cannot hold several values without breaking 1NF. So we create a new relation (entity key, attribute value) with the entity key as a foreign key.")
_q("Easy", "ER to relational", "How is an M:N relationship implemented in a relational database?",
   ["Add a foreign key to either table", "Merge both tables", "Create a junction (associative) table containing both keys", "Use a multivalued attribute"], 2,
   "A foreign key on one side can only point to one row. A junction table with (key of A, key of B) stores any number of pairs.")
_q("Medium", "ER to relational", "Dept (1) - Employee (N) is a relationship with its own attribute 'since'. In the relational schema 'since' is stored in:",
   ["The Dept table", "The Employee table", "Always a new third table", "Both tables"], 1,
   "For a 1:N relationship the foreign key goes to the N side (Employee), so the relationship's own attributes go there too.")
_q("Medium", "ER to relational", "A ternary M:N:N relationship connects three entity sets, each with a simple key. The minimum number of relations is:",
   ["1", "2", "3", "4"], 3,
   "One relation per entity set (3) plus one relation for the ternary relationship holding the three keys = 4.")
_q("Medium", "ER to relational", "Superclass S has subclasses S1 and S2. If one relation is made for S and one for each subclass, the number of relations is:",
   ["1", "2", "3", "4"], 2,
   "1 (superclass) + 2 (subclasses) = 3. Each subclass relation holds the superclass key plus its own attributes.")
_q("Hard", "ER to relational", "Strong entity sets S1 (key k1) and S2 (key k2) are in an M:N relationship R with attribute c. S1 also has a multivalued attribute m. The minimum number of relations is:",
   ["3", "4", "5", "6"], 1,
   "S1 = 1, S2 = 2, R (with c) = 3, and the multivalued attribute m needs its own relation = 4.")

# ---------------- Specialization / generalization ----------------
_q("Easy", "EER", "Defining sub-classes from a general entity set (top-down) is called:",
   ["Generalization", "Specialization", "Aggregation", "Normalization"], 1,
   "Specialization works top-down, splitting a general entity set into more specific ones. Generalization is the bottom-up reverse.")
_q("Easy", "EER", "Combining several entity sets that share common features into a higher-level entity set (bottom-up) is:",
   ["Specialization", "Decomposition", "Generalization", "Projection"], 2,
   "Bottom-up grouping of similar entity sets under one superclass is generalization.")
_q("Medium", "EER", "In a disjoint specialization, an entity of the superclass can belong to:",
   ["At most one subclass", "Several subclasses", "All subclasses", "No superclass"], 0,
   "'Disjoint' means the subclasses do not overlap, so each superclass entity belongs to at most one of them.")

# ---------------- Keys and integrity ----------------
_q("Easy", "Keys", "Which of the following cannot be part of a primary key?",
   ["A column with unique values", "A column containing NULL values", "A composite of two columns", "A column of integer type"], 1,
   "Entity integrity forbids NULL in any primary key attribute.")
_q("Easy", "Keys", "A foreign key must either be NULL or match a value in:",
   ["Any column of any table", "The primary (or candidate) key of the referenced table", "The same row's primary key", "A derived attribute"], 1,
   "That is the definition of referential integrity.")
_q("Easy", "Keys", "Entity integrity rule states that:",
   ["Foreign keys cannot be NULL", "Primary key attributes cannot be NULL", "Every table must have a foreign key", "Tuples must be sorted"], 1,
   "Entity integrity: no attribute of a primary key may be NULL.")
_q("Easy", "Keys", "Referential integrity ensures that:",
   ["Duplicate rows are removed", "Foreign key values refer to existing primary key values or are NULL", "The primary key is always an integer", "Tables are normalized"], 1,
   "It prevents dangling references.")
_q("Easy", "Keys", "A minimal super key is called a:",
   ["Foreign key", "Candidate key", "Alternate attribute", "Surrogate key"], 1,
   "A super key with no removable attribute is a candidate key.")
_q("Medium", "Keys", "R(A, B, C) has A as its only candidate key. The number of super keys of R is:",
   ["2", "3", "4", "8"], 2,
   "Every super key must contain A. B and C are each optional: 2 x 2 = 4. They are {A}, {A,B}, {A,C} and {A,B,C}.")

# ---------------- Normalization and functional dependencies ----------------
_q("Easy", "Normalization", "Which normal form requires every attribute value to be atomic?",
   ["1NF", "2NF", "3NF", "BCNF"], 0,
   "First normal form disallows repeating groups and multi-valued cells.")
_q("Easy", "Normalization", "A Student table has a CourseList column holding 'DB, OS, CN' in one cell. This violates:",
   ["2NF", "3NF", "1NF", "BCNF"], 2,
   "The cell holds several values, so the attribute is not atomic. That breaks 1NF. The fix is a separate Enrollment table.")
_q("Easy", "Normalization", "Second normal form removes:",
   ["Transitive dependencies", "Partial dependencies on part of a composite key", "Multivalued dependencies", "Join dependencies"], 1,
   "2NF: no non-prime attribute depends on only part of a candidate key.")
_q("Easy", "Normalization", "Third normal form removes:",
   ["Partial dependencies", "Repeating groups", "Transitive dependencies of non-key attributes on the key", "Candidate keys"], 2,
   "3NF: non-prime attributes must depend directly on the key, not through another non-key attribute.")
_q("Easy", "Normalization", "If X -> Y and Y -> Z, then X -> Z. This is which of Armstrong's rules?",
   ["Reflexivity", "Augmentation", "Transitivity", "Union"], 2,
   "That is the transitivity rule.")
_q("Medium", "Normalization", "A relation has a partial dependency but all attributes are atomic. It is in:",
   ["1NF but not 2NF", "2NF but not 3NF", "3NF", "BCNF"], 0,
   "Atomic values give 1NF. A partial dependency means 2NF is violated.")
_q("Medium", "Normalization", "A relation is in BCNF if, for every non-trivial dependency X -> Y:",
   ["Y is a prime attribute", "X is a super key", "X is a single attribute", "Y is part of X only"], 1,
   "BCNF is stricter than 3NF: every determinant must be a super key.")
_q("Medium", "Normalization", "R is decomposed into R1 and R2. The decomposition is lossless if R1 intersect R2:",
   ["Is empty", "Functionally determines all attributes of R1 or all attributes of R2 (is a super key of one of them)", "Contains only non-key attributes", "Equals R"], 1,
   "The standard lossless-join test: (R1 intersect R2) -> R1 or (R1 intersect R2) -> R2 must hold.")
_q("Medium", "Normalization", "R(A,B,C,D) has functional dependencies A->B, B->C and C->D. The highest normal form of R is:",
   ["1NF", "2NF", "3NF", "BCNF"], 1,
   "Step 1: A+ = ABCD, so A is the only candidate key.\nStep 2: The key is a single attribute, so there are no partial dependencies and R is in 2NF.\nStep 3: B->C has a non-key determinant and a non-prime dependent, so 3NF fails.")
_q("Hard", "Normalization", "R(A,B,C) has FDs AB -> C and C -> A. Which statement is true?",
   ["R is in BCNF", "R is in 3NF but not in BCNF", "R is in 2NF but not in 3NF", "R is only in 1NF"], 1,
   "Step 1: AB+ = ABC and BC+ = ABC (C->A). Candidate keys: AB and BC.\nStep 2: Every attribute is prime, so 3NF holds.\nStep 3: In C -> A, C is not a super key, so BCNF fails.")
_q("Hard", "Normalization", "R(A,B,C,D) has FDs A->B, B->C, C->D and D->A. The number of candidate keys is:",
   ["1", "2", "3", "4"], 3,
   "Each attribute determines the next one around the cycle, so A+, B+, C+ and D+ are all ABCD. Each single attribute is a candidate key: 4 keys.")
_q("Hard", "Normalization", "R(A,B,C,D,E) has FDs A->B, BC->E and ED->A. The number of candidate keys is:",
   ["2", "3", "4", "5"], 1,
   "Step 1: C and D never appear on a right-hand side, so they are in every key.\nStep 2: CD+ = CD, so add one more attribute.\nStep 3: ACD: A->B gives B, BC->E gives E, so all attributes. Key.\nStep 4: BCD: BC->E, ED->A, so all. Key.\nStep 5: CDE: ED->A, A->B, so all. Key.\nTotal = 3.")
_q("Hard", "Normalization", "R(A,B,C,D) has FDs AB->C, C->D and D->A. The number of candidate keys is:",
   ["1", "2", "3", "4"], 2,
   "B never appears on a right-hand side, so B is in every key.\nAB+ = ABCD (AB->C, C->D). Key.\nBC+ = ABCD (C->D, D->A, then AB->C). Key.\nBD+ = ABCD (D->A, then AB->C, C->D). Key.\nTotal = 3.")
_q("Hard", "Normalization", "R(A,B,C,D) has FDs A->B and C->D. What is the candidate key and the highest normal form?",
   ["AC; 1NF", "A; 2NF", "AC; 2NF", "ABCD; BCNF"], 0,
   "A and C never appear on a right-hand side, so the key must include both: AC+ = ABCD.\nA->B and C->D are partial dependencies on part of the key, so 2NF fails. With atomic values, R is in 1NF.")

# ---------------- Design errors (ties to the project) ----------------
_q("Medium", "Design errors", "Orders stores total_amount although it can be computed as SUM(quantity x unit_price) from OrderItem. This attribute is:",
   ["A multivalued attribute", "A derived (redundant) attribute that risks update anomalies", "A weak entity", "A foreign key"], 1,
   "Stored derived values can drift out of sync with the data they come from. Prefer computing them in a query or a view.")


# ---------------- finish: number the questions, rotate text options ----------------
def _build():
    out = []
    for i, q in enumerate(_RAW, start=1):
        opts, ans = list(q["options"]), q["answer"]
        numeric = all(o.strip().isdigit() for o in opts)
        if not numeric:
            shift = i % 4
            opts = opts[-shift:] + opts[:-shift] if shift else opts
            ans = (ans + shift) % 4
        out.append({**q, "id": i, "options": opts, "answer": ans})
    return out


QUESTIONS = _build()
