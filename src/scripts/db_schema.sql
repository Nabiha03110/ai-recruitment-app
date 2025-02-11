CREATE TABLE chat_history (
    chat_history_turn_id integer NOT NULL,
    interview_id integer,
    question_id integer,
    candidate_answer text,
    PRIMARY KEY (chat_history_turn_id),
    FOREIGN KEY (interview_id) REFERENCES interview(interview_id),
    FOREIGN KEY (question_id) REFERENCES question(question_id)
);

CREATE TABLE criterion (
    criterion_id integer NOT NULL,
    criterion text,
    question_type_id integer,
    PRIMARY KEY (criterion_id),
    FOREIGN KEY (question_type_id) REFERENCES question_type(question_type_id)
);

CREATE TABLE final_evaluation (
    final_evaluation_id integer NOT NULL,
    interview_id integer,
    final_evaluation_json text,
    final_feedback text,
    PRIMARY KEY (final_evaluation_id),
    FOREIGN KEY (interview_id) REFERENCES interview(interview_id)
);

CREATE TABLE interview (
    interview_id integer NOT NULL,
    user_id integer,
    interview_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    interview_recording_url text,
    PRIMARY KEY (interview_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE interview_question (
    interview_id integer NOT NULL,
    question_id integer NOT NULL,
    PRIMARY KEY (interview_id, question_id),
    FOREIGN KEY (interview_id) REFERENCES interview(interview_id),
    FOREIGN KEY (question_id) REFERENCES question(question_id)
);

CREATE TABLE interview_question_evaluation (
    question_evaluation_id integer NOT NULL,
    interview_id integer,
    question_id integer,
    score double precision,
    question_evaluation_json text,
    PRIMARY KEY (question_evaluation_id),
    FOREIGN KEY (interview_id) REFERENCES interview(interview_id),
    FOREIGN KEY (question_id) REFERENCES question(question_id)
);

CREATE TABLE subcriterion (
    subcriterion_id integer NOT NULL,
    subcriterion character varying(255) NOT NULL,
    criterion_id integer,
    question_id integer,
    weight integer,
    PRIMARY KEY (subcriterion_id),
    FOREIGN KEY (criterion_id) REFERENCES criterion(criterion_id),
    FOREIGN KEY (question_id) REFERENCES question(question_id)
);

CREATE TABLE question_type (
    question_type_id INT PRIMARY KEY,
    question_type VARCHAR(100) NOT NULL
    FOREIGN KEY (question_type_id) REFERENCES question_type (question_type_id)
);


CREATE TABLE question (
    question_id integer NOT NULL,
    question text NOT NULL,
    question_type character varying(100) NOT NULL,
    question_type_id integer NOT NULL,
    PRIMARY KEY (question_id)
);

CREATE TABLE users (
    user_id integer NOT NULL,
    name character varying(255) NOT NULL,
    PRIMARY KEY (user_id)
);

CREATE TABLE organization (
    organization_id SERIAL PRIMARY KEY,
    organization VARCHAR(255) NOT NULL
);

CREATE TABLE role_profile (
    role_profile_id SERIAL PRIMARY KEY,
    role_profile VARCHAR(255) NOT NULL,
    organization_id INT NOT NULL,
    level TEXT,
    CONSTRAINT fk_organization
        FOREIGN KEY (organization_id)
        REFERENCES organization (organization_id)
        ON DELETE CASCADE
);

CREATE TABLE role_profile_criterion_weight (
    role_profile_id INT PRIMARY KEY,
    criterion_weight_json TEXT NOT NULL,
    CONSTRAINT fk_role_profile
        FOREIGN KEY (role_profile_id)
        REFERENCES role_profile (role_profile_id)
        ON DELETE CASCADE
);

