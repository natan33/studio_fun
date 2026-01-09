--
-- PostgreSQL database dump
--

\restrict NLHxhs7TPPmK0y5ifGNj5i318XgAEH538MpARcpPf0hP55HLAg79TaRGmSphQyG

-- Dumped from database version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: academy; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA academy;


ALTER SCHEMA academy OWNER TO postgres;

--
-- Name: core; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA core;


ALTER SCHEMA core OWNER TO postgres;

--
-- Name: finance; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA finance;


ALTER SCHEMA finance OWNER TO postgres;

--
-- Name: students; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA students;


ALTER SCHEMA students OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: activities; Type: TABLE; Schema: academy; Owner: natan33
--

CREATE TABLE academy.activities (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text,
    update_at timestamp without time zone,
    status character varying(20)
);


ALTER TABLE academy.activities OWNER TO natan33;

--
-- Name: activities_id_seq; Type: SEQUENCE; Schema: academy; Owner: natan33
--

CREATE SEQUENCE academy.activities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE academy.activities_id_seq OWNER TO natan33;

--
-- Name: activities_id_seq; Type: SEQUENCE OWNED BY; Schema: academy; Owner: natan33
--

ALTER SEQUENCE academy.activities_id_seq OWNED BY academy.activities.id;


--
-- Name: attendance; Type: TABLE; Schema: academy; Owner: natan33
--

CREATE TABLE academy.attendance (
    id integer NOT NULL,
    student_id integer NOT NULL,
    schedule_id integer NOT NULL,
    date date NOT NULL,
    created_at timestamp without time zone,
    status character varying(20)
);


ALTER TABLE academy.attendance OWNER TO natan33;

--
-- Name: attendance_id_seq; Type: SEQUENCE; Schema: academy; Owner: natan33
--

CREATE SEQUENCE academy.attendance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE academy.attendance_id_seq OWNER TO natan33;

--
-- Name: attendance_id_seq; Type: SEQUENCE OWNED BY; Schema: academy; Owner: natan33
--

ALTER SEQUENCE academy.attendance_id_seq OWNED BY academy.attendance.id;


--
-- Name: attendance_summary; Type: TABLE; Schema: academy; Owner: natan33
--

CREATE TABLE academy.attendance_summary (
    id integer NOT NULL,
    student_id integer,
    total_lessons integer,
    last_presence date,
    created_at timestamp without time zone,
    update_at timestamp without time zone
);


ALTER TABLE academy.attendance_summary OWNER TO natan33;

--
-- Name: attendance_summary_id_seq; Type: SEQUENCE; Schema: academy; Owner: natan33
--

CREATE SEQUENCE academy.attendance_summary_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE academy.attendance_summary_id_seq OWNER TO natan33;

--
-- Name: attendance_summary_id_seq; Type: SEQUENCE OWNED BY; Schema: academy; Owner: natan33
--

ALTER SEQUENCE academy.attendance_summary_id_seq OWNED BY academy.attendance_summary.id;


--
-- Name: class_schedule; Type: TABLE; Schema: academy; Owner: natan33
--

CREATE TABLE academy.class_schedule (
    id integer NOT NULL,
    day_of_week character varying(100) NOT NULL,
    start_time time without time zone NOT NULL,
    max_capacity integer,
    created_at timestamp without time zone,
    update_at timestamp without time zone,
    activity_id integer NOT NULL,
    status character varying(20),
    is_active boolean
);


ALTER TABLE academy.class_schedule OWNER TO natan33;

--
-- Name: class_schedule_id_seq; Type: SEQUENCE; Schema: academy; Owner: natan33
--

CREATE SEQUENCE academy.class_schedule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE academy.class_schedule_id_seq OWNER TO natan33;

--
-- Name: class_schedule_id_seq; Type: SEQUENCE OWNED BY; Schema: academy; Owner: natan33
--

ALTER SEQUENCE academy.class_schedule_id_seq OWNED BY academy.class_schedule.id;


--
-- Name: class_students; Type: TABLE; Schema: academy; Owner: natan33
--

CREATE TABLE academy.class_students (
    student_id integer NOT NULL,
    class_id integer NOT NULL,
    enrolled_at timestamp without time zone,
    created_at timestamp without time zone,
    update_at timestamp without time zone
);


ALTER TABLE academy.class_students OWNER TO natan33;

--
-- Name: enrollments; Type: TABLE; Schema: academy; Owner: natan33
--

CREATE TABLE academy.enrollments (
    id integer NOT NULL,
    student_id integer NOT NULL,
    schedule_id integer NOT NULL,
    enrollment_date timestamp without time zone,
    status character varying(20),
    created_at timestamp without time zone,
    update_at timestamp without time zone
);


ALTER TABLE academy.enrollments OWNER TO natan33;

--
-- Name: enrollments_id_seq; Type: SEQUENCE; Schema: academy; Owner: natan33
--

CREATE SEQUENCE academy.enrollments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE academy.enrollments_id_seq OWNER TO natan33;

--
-- Name: enrollments_id_seq; Type: SEQUENCE OWNED BY; Schema: academy; Owner: natan33
--

ALTER SEQUENCE academy.enrollments_id_seq OWNED BY academy.enrollments.id;


--
-- Name: modalities; Type: TABLE; Schema: academy; Owner: natan33
--

CREATE TABLE academy.modalities (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text,
    created_at timestamp without time zone,
    update_at timestamp without time zone
);


ALTER TABLE academy.modalities OWNER TO natan33;

--
-- Name: modalities_id_seq; Type: SEQUENCE; Schema: academy; Owner: natan33
--

CREATE SEQUENCE academy.modalities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE academy.modalities_id_seq OWNER TO natan33;

--
-- Name: modalities_id_seq; Type: SEQUENCE OWNED BY; Schema: academy; Owner: natan33
--

ALTER SEQUENCE academy.modalities_id_seq OWNED BY academy.modalities.id;


--
-- Name: audit_logs; Type: TABLE; Schema: core; Owner: natan33
--

CREATE TABLE core.audit_logs (
    id integer NOT NULL,
    user_id integer,
    action character varying(100),
    table_name character varying(50),
    old_value json,
    new_value json,
    created_at timestamp without time zone,
    update_at timestamp without time zone
);


ALTER TABLE core.audit_logs OWNER TO natan33;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: core; Owner: natan33
--

CREATE SEQUENCE core.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE core.audit_logs_id_seq OWNER TO natan33;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: core; Owner: natan33
--

ALTER SEQUENCE core.audit_logs_id_seq OWNED BY core.audit_logs.id;


--
-- Name: settings; Type: TABLE; Schema: core; Owner: natan33
--

CREATE TABLE core.settings (
    id integer NOT NULL,
    key character varying(50),
    value text,
    created_at timestamp without time zone,
    update_at timestamp without time zone
);


ALTER TABLE core.settings OWNER TO natan33;

--
-- Name: settings_id_seq; Type: SEQUENCE; Schema: core; Owner: natan33
--

CREATE SEQUENCE core.settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE core.settings_id_seq OWNER TO natan33;

--
-- Name: settings_id_seq; Type: SEQUENCE OWNED BY; Schema: core; Owner: natan33
--

ALTER SEQUENCE core.settings_id_seq OWNED BY core.settings.id;


--
-- Name: welcome_email_logs; Type: TABLE; Schema: core; Owner: natan33
--

CREATE TABLE core.welcome_email_logs (
    id integer NOT NULL,
    student_id integer NOT NULL,
    created_at timestamp without time zone,
    update_at timestamp without time zone
);


ALTER TABLE core.welcome_email_logs OWNER TO natan33;

--
-- Name: welcome_email_logs_id_seq; Type: SEQUENCE; Schema: core; Owner: natan33
--

CREATE SEQUENCE core.welcome_email_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE core.welcome_email_logs_id_seq OWNER TO natan33;

--
-- Name: welcome_email_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: core; Owner: natan33
--

ALTER SEQUENCE core.welcome_email_logs_id_seq OWNED BY core.welcome_email_logs.id;


--
-- Name: expenses; Type: TABLE; Schema: finance; Owner: natan33
--

CREATE TABLE finance.expenses (
    id integer NOT NULL,
    description character varying(150) NOT NULL,
    category character varying(50) NOT NULL,
    amount numeric(10,2) NOT NULL,
    due_date date NOT NULL,
    payment_date date,
    status character varying(20),
    observation text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE finance.expenses OWNER TO natan33;

--
-- Name: expenses_id_seq; Type: SEQUENCE; Schema: finance; Owner: natan33
--

CREATE SEQUENCE finance.expenses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE finance.expenses_id_seq OWNER TO natan33;

--
-- Name: expenses_id_seq; Type: SEQUENCE OWNED BY; Schema: finance; Owner: natan33
--

ALTER SEQUENCE finance.expenses_id_seq OWNED BY finance.expenses.id;


--
-- Name: invoices; Type: TABLE; Schema: finance; Owner: natan33
--

CREATE TABLE finance.invoices (
    id integer NOT NULL,
    student_id integer,
    due_date date NOT NULL,
    status character varying(20),
    created_at timestamp without time zone,
    plan_id integer,
    amount numeric(10,2) NOT NULL,
    payment_date timestamp without time zone,
    payment_method character varying(20),
    external_id character varying(100),
    pix_copy_paste text,
    update_at timestamp without time zone,
    paid_at timestamp without time zone,
    description_paid text
);


ALTER TABLE finance.invoices OWNER TO natan33;

--
-- Name: invoices_id_seq; Type: SEQUENCE; Schema: finance; Owner: natan33
--

CREATE SEQUENCE finance.invoices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE finance.invoices_id_seq OWNER TO natan33;

--
-- Name: invoices_id_seq; Type: SEQUENCE OWNED BY; Schema: finance; Owner: natan33
--

ALTER SEQUENCE finance.invoices_id_seq OWNED BY finance.invoices.id;


--
-- Name: plans; Type: TABLE; Schema: finance; Owner: natan33
--

CREATE TABLE finance.plans (
    id integer NOT NULL,
    name character varying(50),
    price numeric(10,2) NOT NULL,
    duration_days integer,
    created_at timestamp without time zone,
    update_at timestamp without time zone,
    duration_months integer
);


ALTER TABLE finance.plans OWNER TO natan33;

--
-- Name: plans_id_seq; Type: SEQUENCE; Schema: finance; Owner: natan33
--

CREATE SEQUENCE finance.plans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE finance.plans_id_seq OWNER TO natan33;

--
-- Name: plans_id_seq; Type: SEQUENCE OWNED BY; Schema: finance; Owner: natan33
--

ALTER SEQUENCE finance.plans_id_seq OWNED BY finance.plans.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: natan33
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO natan33;

--
-- Name: registrations; Type: TABLE; Schema: public; Owner: natan33
--

CREATE TABLE public.registrations (
    id integer NOT NULL,
    user_id integer NOT NULL,
    status character varying(20),
    created_at timestamp without time zone,
    update_at timestamp without time zone,
    last_seen_at timestamp without time zone,
    is_active boolean
);


ALTER TABLE public.registrations OWNER TO natan33;

--
-- Name: registrations_id_seq; Type: SEQUENCE; Schema: public; Owner: natan33
--

CREATE SEQUENCE public.registrations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.registrations_id_seq OWNER TO natan33;

--
-- Name: registrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: natan33
--

ALTER SEQUENCE public.registrations_id_seq OWNED BY public.registrations.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: natan33
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(255) NOT NULL,
    is_active boolean,
    created_at timestamp without time zone,
    last_seen_at timestamp without time zone,
    reset_code character varying(100)
);


ALTER TABLE public.users OWNER TO natan33;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: natan33
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO natan33;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: natan33
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: student_health_data; Type: TABLE; Schema: students; Owner: natan33
--

CREATE TABLE students.student_health_data (
    id integer NOT NULL,
    student_id integer,
    blood_type character varying(3),
    medical_notes text,
    weight double precision,
    created_at timestamp without time zone,
    update_at timestamp without time zone,
    height double precision
);


ALTER TABLE students.student_health_data OWNER TO natan33;

--
-- Name: student_health_data_id_seq; Type: SEQUENCE; Schema: students; Owner: natan33
--

CREATE SEQUENCE students.student_health_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE students.student_health_data_id_seq OWNER TO natan33;

--
-- Name: student_health_data_id_seq; Type: SEQUENCE OWNED BY; Schema: students; Owner: natan33
--

ALTER SEQUENCE students.student_health_data_id_seq OWNED BY students.student_health_data.id;


--
-- Name: students; Type: TABLE; Schema: students; Owner: natan33
--

CREATE TABLE students.students (
    id integer NOT NULL,
    full_name character varying NOT NULL,
    cpf character varying(14),
    birth_date date,
    created_at timestamp without time zone,
    update_at timestamp without time zone,
    email character varying(120),
    phone character varying(20),
    is_active boolean,
    blood_type character varying(5),
    weight double precision,
    height double precision,
    medical_notes text,
    emergency_contact character varying(100),
    emergency_phone character varying(20),
    postal_code character varying(10),
    address character varying(150),
    address_number character varying(10),
    city character varying(50),
    plan_id integer
);


ALTER TABLE students.students OWNER TO natan33;

--
-- Name: students_id_seq; Type: SEQUENCE; Schema: students; Owner: natan33
--

CREATE SEQUENCE students.students_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE students.students_id_seq OWNER TO natan33;

--
-- Name: students_id_seq; Type: SEQUENCE OWNED BY; Schema: students; Owner: natan33
--

ALTER SEQUENCE students.students_id_seq OWNED BY students.students.id;


--
-- Name: activities id; Type: DEFAULT; Schema: academy; Owner: natan33
--

ALTER TABLE ONLY academy.activities ALTER COLUMN id SET DEFAULT nextval('academy.activities_id_seq'::regclass);


--
-- Name: attendance id; Type: DEFAULT; Schema: academy; Owner: natan33
--

ALTER TABLE ONLY academy.attendance ALTER COLUMN id SET DEFAULT nextval('academy.attendance_id_seq'::regclass);


--
-- Name: attendance_summary id; Type: DEFAULT; Schema: academy; Owner: natan33
--

ALTER TABLE ONLY academy.attendance_summary ALTER COLUMN id SET DEFAULT nextval('academy.attendance_summary_id_seq'::regclass);


--
-- Name: class_schedule id; Type: DEFAULT; Schema: academy; Owner: natan33
--

ALTER TABLE ONLY academy.class_schedule ALTER COLUMN id SET DEFAULT nextval('academy.class_schedule_id_seq'::regclass);


--
-- Name: enrollments id; Type: DEFAULT; Schema: academy; Owner: natan33
--

ALTER TABLE ONLY academy.enrollments ALTER COLUMN id SET DEFAULT nextval('academy.enrollments_id_seq'::regclass);


--
-- Name: modalities id; Type: DEFAULT; Schema: academy; Owner: natan33
--

ALTER TABLE ONLY academy.modalities ALTER COLUMN id SET DEFAULT nextval('academy.modalities_id_seq'::regclass);


--
-- Name: audit_logs id; Type: DEFAULT; Schema: core; Owner: natan33
--

ALTER TABLE ONLY core.audit_logs ALTER COLUMN id SET DEFAULT nextval('core.audit_logs_id_seq'::regclass);


--
-- Name: settings id; Type: DEFAULT; Schema: core; Owner: natan33
--

ALTER TABLE ONLY core.settings ALTER COLUMN id SET DEFAULT nextval('core.settings_id_seq'::regclass);


--
-- Name: welcome_email_logs id; Type: DEFAULT; Schema: core; Owner: natan33
--

ALTER TABLE ONLY core.welcome_email_logs ALTER COLUMN id SET DEFAULT nextval('core.welcome_email_logs_id_seq'::regclass);


--
-- Name: expenses id; Type: DEFAULT; Schema: finance; Owner: natan33
--

ALTER TABLE ONLY finance.expenses ALTER COLUMN id SET DEFAULT nextval('finance.expenses_id_seq'::regclass);


--
-- Name: invoices id; Type: DEFAULT; Schema: finance; Owner: natan33
--

ALTER TABLE ONLY finance.invoices ALTER COLUMN id SET DEFAULT nextval('finance.invoices_id_seq'::regclass);


--
-- Name: plans id; Type: DEFAULT; Schema: finance; Owner: natan33
--

ALTER TABLE ONLY finance.plans ALTER COLUMN id SET DEFAULT nextval('finance.plans_id_seq'::regclass);


--
-- Name: registrations id; Type: DEFAULT; Schema: public; Owner: natan33
--

ALTER TABLE ONLY public.registrations ALTER COLUMN id SET DEFAULT nextval('public.registrations_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: natan33
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: student_health_data id; Type: DEFAULT; Schema: students; Owner: natan33
--

ALTER TABLE ONLY students.student_health_data ALTER COLUMN id SET DEFAULT nextval('students.student_health_data_id_seq'::regclass);


--
-- Name: students id; Type: DEFAULT; Schema: students; Owner: natan33
--

ALTER TABLE ONLY students.students ALTER COLUMN id SET DEFAULT nextval('students.students_id_seq'::regclass);


--
-- Data for Name: activities; Type: TABLE DATA; Schema: academy; Owner: natan33
--

COPY academy.activities (id, name, description, update_at, status) FROM stdin;
1	Zumba	Aula de Zumba	2026-01-02 10:21:16.787476	Ativo
3	Funcional	Aula de Funcional	2026-01-02 11:49:33.534579	Ativo
4	Multifuncional	Aula de Multifuncional as segundas, quartas, quintas e sextas 	2026-01-02 12:10:01.261201	Ativo
5	Aerohit	Aula de Aerohit nos dias:\r\nterças e quintas às 19:00 horas\r\nsábados às 08:00 horas	2026-01-02 12:11:01.012621	Ativo
2	Pilates	Aula de Pliates	2026-01-02 12:11:18.067894	Ativo
6	Dança Aeróbica	Aula de Dança Aeróbica as sábados as 09:00 horas	2026-01-02 12:12:01.112657	Ativo
7	RitBox	Todos os sábados as 10:00	2026-01-02 18:44:24.519762	Ativo
8	step	Aula de step	2026-01-06 15:25:09.12837	Ativo
9	Programa de Emagrecimento	Programa de Emagrecimento	2026-01-06 16:03:27.475857	Ativo
10	Aula Coletiva	Aula Coletiva	2026-01-06 18:11:58.766117	Ativo
11	GAP	Aula de GAP	2026-01-06 18:34:35.150399	Ativo
\.


--
-- Data for Name: attendance; Type: TABLE DATA; Schema: academy; Owner: natan33
--

COPY academy.attendance (id, student_id, schedule_id, date, created_at, status) FROM stdin;
3	4	10	2026-01-02	2026-01-02 14:32:32.147381	Justificado
1	3	9	2026-01-02	2026-01-02 13:22:59.021459	Justificado
2	5	9	2026-01-02	2026-01-02 13:23:12.859254	Justificado
4	4	28	2026-01-04	2026-01-04 18:18:37.855379	Justificado
6	5	32	2026-01-06	2026-01-06 13:51:21.299978	Presente
5	3	32	2026-01-06	2026-01-06 13:51:18.954861	Presente
7	6	44	2026-01-06	2026-01-06 16:05:17.220336	Presente
\.


--
-- Data for Name: attendance_summary; Type: TABLE DATA; Schema: academy; Owner: natan33
--

COPY academy.attendance_summary (id, student_id, total_lessons, last_presence, created_at, update_at) FROM stdin;
\.


--
-- Data for Name: class_schedule; Type: TABLE DATA; Schema: academy; Owner: natan33
--

COPY academy.class_schedule (id, day_of_week, start_time, max_capacity, created_at, update_at, activity_id, status, is_active) FROM stdin;
9	Segunda-feira	18:10:00	15	2025-12-29 13:05:42.760643	2026-01-02 18:31:49.723618	3	\N	f
10	Segunda-feira	17:20:00	15	2025-12-29 13:30:00.688258	2026-01-02 18:33:23.483143	3	\N	f
28	Segunda, Quarta e Sexta	16:30:00	15	2026-01-02 18:37:40.39583	2026-01-02 18:37:40.395838	3	Ativo	t
29	Segunda, Quarta e Sexta	18:10:00	15	2026-01-02 18:37:58.081383	2026-01-02 18:37:58.081392	3	Ativo	t
31	Segunda, Quarta e Sexta	14:50:00	15	2026-01-02 18:38:32.194507	2026-01-02 18:38:32.194513	4	Ativo	t
32	Segunda, Quarta e Sexta	19:00:00	15	2026-01-02 18:39:14.545422	2026-01-02 18:39:14.545432	4	Ativo	t
33	Terça e Quinta	15:50:00	15	2026-01-02 18:41:27.439058	2026-01-02 18:41:27.439067	2	Ativo	t
34	Terça e Quinta	16:40:00	15	2026-01-02 18:41:42.038936	2026-01-02 18:41:42.038941	2	Ativo	t
35	Terça e Quinta	17:30:00	15	2026-01-02 18:42:00.774915	2026-01-02 18:42:00.77492	3	Ativo	t
36	Terça e Quinta	18:20:00	15	2026-01-02 18:42:25.89163	2026-01-02 18:42:25.891637	3	Ativo	t
38	Terça e Quinta	19:10:00	15	2026-01-02 18:43:08.793958	2026-01-02 18:43:08.793969	5	Ativo	t
39	Sábado	08:00:00	15	2026-01-02 18:43:28.10243	2026-01-02 18:43:28.102441	5	Ativo	t
40	Sábado	09:00:00	15	2026-01-02 18:43:40.270128	2026-01-02 18:43:40.270134	6	Ativo	t
42	Sábado	11:00:00	15	2026-01-02 18:44:57.954405	2026-01-02 18:44:57.954426	3	Ativo	t
37	Terça e Quinta	14:00:00	15	2026-01-02 18:42:47.110072	2026-01-02 18:53:14.470659	4	Ativo	t
30	Segunda, Quarta e Sexta	14:00:00	15	2026-01-02 18:38:16.613206	2026-01-02 18:53:23.736779	4	Ativo	f
27	Segunda à Sexta	15:40:00	15	2026-01-02 18:13:57.276952	2026-01-06 15:26:24.087409	3	Ativo	\N
43	Segunda à Sexta	17:20:00	15	2026-01-06 15:40:12.150935	2026-01-06 15:40:12.150946	3	Ativo	t
44	Segunda à Sábado	14:40:00	15	2026-01-06 16:04:03.997273	2026-01-06 16:04:03.997277	9	Ativo	t
45	Segunda à Sexta	19:00:00	15	2026-01-06 17:54:04.728186	2026-01-06 18:00:25.036558	3	Ativo	t
46	Terça e Quinta	18:00:00	15	2026-01-06 18:12:30.454592	2026-01-06 18:12:30.454604	10	Ativo	t
47	Terça e Quinta	09:00:00	15	2026-01-06 18:12:52.065235	2026-01-06 18:12:52.065244	10	Ativo	t
41	Terça e Quinta	07:00:00	15	2026-01-02 18:44:42.180737	2026-01-06 18:14:05.781215	7	Ativo	t
48	Terça e Quinta	18:00:00	15	2026-01-06 18:35:09.779394	2026-01-06 18:35:09.779414	11	Ativo	t
\.


--
-- Data for Name: class_students; Type: TABLE DATA; Schema: academy; Owner: natan33
--

COPY academy.class_students (student_id, class_id, enrolled_at, created_at, update_at) FROM stdin;
\.


--
-- Data for Name: enrollments; Type: TABLE DATA; Schema: academy; Owner: natan33
--

COPY academy.enrollments (id, student_id, schedule_id, enrollment_date, status, created_at, update_at) FROM stdin;
17	3	32	2026-01-06 13:36:31.96002	Ativo	2026-01-06 13:36:31.980265	2026-01-06 13:36:31.980269
18	4	43	2026-01-06 15:40:43.994164	Ativo	2026-01-06 15:40:44.019563	2026-01-06 15:40:44.019568
19	6	44	2026-01-06 16:04:32.501872	Ativo	2026-01-06 16:04:32.518467	2026-01-06 16:04:32.518471
20	5	45	2026-01-06 17:54:20.526669	Ativo	2026-01-06 17:54:20.548997	2026-01-06 17:54:20.549002
21	7	45	2026-01-06 18:00:38.163288	Ativo	2026-01-06 18:00:38.17629	2026-01-06 18:00:38.176293
22	8	46	2026-01-06 18:13:22.382422	Ativo	2026-01-06 18:13:22.393385	2026-01-06 18:13:22.393389
23	9	43	2026-01-06 18:16:59.062917	Ativo	2026-01-06 18:16:59.084014	2026-01-06 18:16:59.084017
24	10	43	2026-01-06 18:22:42.362077	Ativo	2026-01-06 18:22:42.377189	2026-01-06 18:22:42.377194
25	11	43	2026-01-06 18:26:43.457532	Ativo	2026-01-06 18:26:43.478646	2026-01-06 18:26:43.478651
\.


--
-- Data for Name: modalities; Type: TABLE DATA; Schema: academy; Owner: natan33
--

COPY academy.modalities (id, name, description, created_at, update_at) FROM stdin;
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: core; Owner: natan33
--

COPY core.audit_logs (id, user_id, action, table_name, old_value, new_value, created_at, update_at) FROM stdin;
\.


--
-- Data for Name: settings; Type: TABLE DATA; Schema: core; Owner: natan33
--

COPY core.settings (id, key, value, created_at, update_at) FROM stdin;
\.


--
-- Data for Name: welcome_email_logs; Type: TABLE DATA; Schema: core; Owner: natan33
--

COPY core.welcome_email_logs (id, student_id, created_at, update_at) FROM stdin;
2	5	2026-01-06 13:32:35.399659	2026-01-06 13:32:35.399666
3	3	2026-01-06 13:36:34.290282	2026-01-06 13:36:34.290287
4	4	2026-01-06 15:40:50.034898	2026-01-06 15:40:50.034904
5	6	2026-01-06 16:04:39.075696	2026-01-06 16:04:39.075703
7	7	2026-01-06 18:00:43.517537	2026-01-06 18:00:43.517545
8	8	2026-01-06 18:13:29.193504	2026-01-06 18:13:29.193507
9	9	2026-01-06 18:17:05.767526	2026-01-06 18:17:05.767531
10	10	2026-01-06 18:22:48.472817	2026-01-06 18:22:48.472824
11	11	2026-01-06 18:26:50.132015	2026-01-06 18:26:50.132021
\.


--
-- Data for Name: expenses; Type: TABLE DATA; Schema: finance; Owner: natan33
--

COPY finance.expenses (id, description, category, amount, due_date, payment_date, status, observation, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: invoices; Type: TABLE DATA; Schema: finance; Owner: natan33
--

COPY finance.invoices (id, student_id, due_date, status, created_at, plan_id, amount, payment_date, payment_method, external_id, pix_copy_paste, update_at, paid_at, description_paid) FROM stdin;
20	3	2026-01-10	cancelled	2026-01-06 09:31:46.504182	1	70.00	2026-01-06 11:56:38.603021	\N	\N	\N	2026-01-06 13:55:01.147688	\N	\N
2	4	2026-01-03	cancelled	2026-01-03 05:05:13.636086	1	70.00	2026-01-03 02:01:39.971329	\N	\N	\N	2026-01-04 16:51:49.685558	\N	\N
1	4	2025-10-05	cancelled	2026-01-03 05:05:13.636079	1	70.00	2026-01-04 12:37:23.327027	\N	\N	\N	2026-01-04 17:00:48.168956	\N	\N
24	4	2026-01-10	cancelled	2026-01-06 09:31:46.504182	1	70.00	\N	\N	\N	\N	2026-01-06 15:44:10.961506	\N	\N
4	5	2026-01-10	cancelled	2026-01-03 05:44:08.891584	1	70.00	\N	\N	\N	\N	2026-01-04 17:04:34.931329	\N	\N
25	3	2026-01-10	cancelled	2026-01-06 13:35:45.746572	1	70.00	\N	\N	\N	\N	2026-01-06 15:44:13.484225	\N	\N
28	4	2026-01-10	pending	2026-01-06 15:19:21.291039	1	70.00	2026-01-06 15:47:38.341474	\N	\N	\N	2026-01-06 16:05:46.625748	\N	\N
27	3	2026-01-10	pending	2026-01-06 15:19:21.291039	1	70.00	2026-01-06 15:46:01.194977	\N	\N	\N	2026-01-06 16:05:51.007725	\N	\N
5	4	2026-01-10	cancelled	2026-01-04 17:47:55.531283	1	70.00	2026-01-05 19:27:43.486953	\N	\N	\N	2026-01-05 22:43:42.998081	\N	\N
7	5	2026-01-10	cancelled	2026-01-04 17:47:55.531283	1	70.00	2026-01-05 19:27:53.15188	\N	\N	\N	2026-01-05 22:43:51.098565	\N	\N
10	4	2026-01-10	cancelled	2026-01-05 22:42:35.662239	1	70.00	\N	\N	\N	\N	2026-01-05 22:48:12.28185	\N	\N
9	5	2026-01-10	cancelled	2026-01-05 22:42:35.662239	1	70.00	\N	\N	\N	\N	2026-01-05 22:48:20.081184	\N	\N
26	5	2026-01-10	pending	2026-01-06 13:35:45.746572	2	210.00	2026-01-06 15:46:35.85954	\N	\N	\N	2026-01-06 16:47:33.315918	2026-01-06 16:46:17.172874	\N
13	4	2026-01-10	cancelled	2026-01-05 22:48:04.329782	1	70.00	\N	\N	\N	\N	2026-01-05 22:50:15.894504	\N	\N
12	5	2026-01-10	cancelled	2026-01-05 22:48:04.329782	1	70.00	\N	\N	\N	\N	2026-01-05 22:50:23.525643	\N	\N
29	6	2026-01-10	paid	2026-01-06 15:19:21.291039	6	150.00	\N	Dinheiro	\N	\N	2026-01-06 17:10:18.609204	2026-01-06 17:10:18.608431	\N
30	7	2026-01-10	pending	2026-01-06 18:05:24.827715	1	70.00	\N	\N	\N	\N	2026-01-06 18:26:57.973863	\N	\N
31	8	2026-01-10	pending	2026-01-06 18:05:24.827715	1	70.00	\N	\N	\N	\N	2026-01-06 18:26:57.992514	\N	\N
32	9	2026-01-10	pending	2026-01-06 18:05:24.827715	1	70.00	\N	\N	\N	\N	2026-01-06 18:26:58.005868	\N	\N
33	10	2026-01-10	pending	2026-01-06 18:05:24.827715	1	70.00	\N	\N	\N	\N	2026-01-06 18:26:58.024973	\N	\N
16	4	2026-01-10	cancelled	2026-01-05 22:51:12.981522	1	70.00	\N	\N	\N	\N	2026-01-06 09:32:58.666375	\N	\N
19	3	2026-01-10	cancelled	2026-01-06 09:31:46.504182	1	70.00	\N	\N	\N	\N	2026-01-06 09:33:03.02242	\N	\N
15	5	2026-01-10	cancelled	2026-01-05 22:51:12.981522	1	70.00	\N	\N	\N	\N	2026-01-06 09:33:06.77228	\N	\N
21	5	2026-01-10	cancelled	2026-01-06 09:31:46.504182	1	70.00	\N	\N	\N	\N	2026-01-06 10:29:57.925896	\N	\N
34	11	2026-01-10	pending	2026-01-06 18:05:24.827715	1	70.00	\N	\N	\N	\N	2026-01-06 18:26:58.043306	\N	\N
22	4	2026-01-10	cancelled	2026-01-06 09:31:46.504182	1	70.00	\N	\N	\N	\N	2026-01-06 11:56:46.348705	\N	\N
23	5	2026-01-10	cancelled	2026-01-06 09:31:46.504182	2	210.00	2026-01-06 11:56:34.133617	\N	\N	\N	2026-01-06 12:00:36.784029	\N	\N
\.


--
-- Data for Name: plans; Type: TABLE DATA; Schema: finance; Owner: natan33
--

COPY finance.plans (id, name, price, duration_days, created_at, update_at, duration_months) FROM stdin;
2	Plano Trimestral	210.00	\N	2026-01-06 10:01:16.941142	2026-01-06 10:58:31.843325	3
1	Plano Mensal	70.00	\N	2026-01-03 01:57:59.618709	2026-01-06 11:02:10.888382	1
4	Plano Quinzenal (15 dias)	35.00	\N	2026-01-06 11:53:19.232153	2026-01-06 11:53:19.232159	1
5	Plano Bimestral (2 meses)	140.00	\N	2026-01-06 11:54:20.03968	2026-01-06 11:54:20.039688	1
3	Plano Anual	1000.00	\N	2026-01-06 10:02:25.331664	2026-01-06 11:55:42.581972	\N
6	Programa de Emagrecimento	150.00	\N	2026-01-06 15:42:32.619686	2026-01-06 15:42:32.619693	1
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: natan33
--

COPY public.alembic_version (version_num) FROM stdin;
1a5328c30b78
\.


--
-- Data for Name: registrations; Type: TABLE DATA; Schema: public; Owner: natan33
--

COPY public.registrations (id, user_id, status, created_at, update_at, last_seen_at, is_active) FROM stdin;
1	1	pending	2025-12-28 16:03:43.398687	2025-12-28 16:03:43.398692	\N	\N
2	2	active	2026-01-06 13:46:16.491262	2026-01-06 13:46:16.491263	2026-01-06 13:46:16.491254	t
3	3	active	2026-01-06 14:19:44.295651	2026-01-06 14:19:44.295654	2026-01-06 14:19:44.295639	t
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: natan33
--

COPY public.users (id, username, email, password_hash, is_active, created_at, last_seen_at, reset_code) FROM stdin;
1	natan33	natansa19@gmail.com	scrypt:32768:8:1$Hc7mYPLroJEgJ3S7$4c12d77e3abbfb0685f3a60958c1966f32182fa715d20748f000e9e3360539ea35e46a8441f71b02331d8e283365a070553a995e1cc9b40024e833a041109464	t	2025-12-28 16:01:17.822447	2026-01-05 00:42:43.001932	\N
2	maila_assis	mailasantos520@gmail.com	scrypt:32768:8:1$rudLc6Bqa9OIzIcs$89b1e25dfcfbf8f8dfbb986eda86b2c3ae20a34ab671c602b8ea3273248a763f7b7253be88cf24df472ea2861df3641db15ccddc2f94bbd4426a6b527ed3444c	t	2026-01-06 13:42:20.741585	2026-01-06 13:42:20.741579	\N
3	gleide.valentino	gleidevalentino@gmail.com	scrypt:32768:8:1$mIX0VSc3vN7iCUx8$3785ce877cf1adf0e401c03364d965530c8ec3982d5237df63110f8b58fc1a87007979c9535c9912a213de38b10f188baca585f9034da000cac7dc78d3292c72	t	2026-01-06 14:19:13.045178	2026-01-06 14:19:13.04517	\N
\.


--
-- Data for Name: student_health_data; Type: TABLE DATA; Schema: students; Owner: natan33
--

COPY students.student_health_data (id, student_id, blood_type, medical_notes, weight, created_at, update_at, height) FROM stdin;
3	4	O+	Aluna Hipertensa	68	2025-12-29 12:09:52.457651	2025-12-29 16:59:25.326698	1.68
4	5	O+	Nenhuma observação.	105	2025-12-29 17:18:13.299725	2025-12-29 17:19:34.203572	1.73
2	3	O+	Alergia ao Cabelo	72	2025-12-29 12:06:17.002516	2025-12-29 17:38:04.598506	1.6
5	6	O+	Esposo da Aluna	\N	2026-01-06 15:58:53.612337	2026-01-06 16:02:23.752382	1.57
6	7	O+	Marido da Aluna	77	2026-01-06 17:59:51.80627	2026-01-06 17:59:51.806276	1.59
7	8	A+	Esposo da Aluna	72.8	2026-01-06 18:10:26.519283	2026-01-06 18:10:26.519286	1.6
8	9	B+	Filho da Aluna	72	2026-01-06 18:16:36.292091	2026-01-06 18:16:36.292094	1.72
9	10	B+	Filha da Aluna	101	2026-01-06 18:22:09.384936	2026-01-06 18:22:09.384938	1.77
10	11	O+	Esposo da Aluna	127	2026-01-06 18:26:25.243438	2026-01-06 18:26:25.243442	1.68
\.


--
-- Data for Name: students; Type: TABLE DATA; Schema: students; Owner: natan33
--

COPY students.students (id, full_name, cpf, birth_date, created_at, update_at, email, phone, is_active, blood_type, weight, height, medical_notes, emergency_contact, emergency_phone, postal_code, address, address_number, city, plan_id) FROM stdin;
3	Maila Dos Santos Pinheiro de Assis	86323025582	1999-04-25	2025-12-29 12:06:16.998311	2026-01-03 02:43:03.067335	mailasantos520@gmail.com	71985130412	t	\N	\N	\N	\N		\N	40732-395	Rua da Ressurreição	520	Salvador	1
4	Jacira Silva de Assis	51224100549	1968-05-05	2025-12-29 12:09:52.455772	2026-01-04 18:21:15.829363	srjacira18@gmail.com	(71)98501-7723	t	\N	\N	\N	\N	Natã (Filho)	71985315982	40750294	Segunda Travessa 16 de Janeiro	21	Salvador	1
5	Natã Silva de Assis	86240113530	2000-01-15	2025-12-29 17:18:13.287101	2026-01-06 15:23:39.640531	natansa19@gmail.com	71985315982	t	\N	\N	\N	\N	---	\N	40732-395	Rua da Ressurreição	520	Salvador	2
6	Mariluce Santos Nascimento	81894481534	1981-08-26	2026-01-06 15:58:53.600943	2026-01-06 16:02:23.746034	81mariluce@gmail.com	71983131195	t	\N	\N	\N	\N	aelson	71991413170	40748-525	Rua do Congo	96	Salvador	6
7	Ana Paula Pereira da Cruz Souza	82567603549	1980-11-26	2026-01-06 17:59:51.800104	2026-01-06 17:59:51.800112	paula_diva2009@hotmail.com	71987083658	t	\N	\N	\N	\N		(71) 98821-6703	40749-010	Rua Franco Velasco	710	Salvador	1
8	Aurea Janan Almeida Leite	02027610537	1985-11-29	2026-01-06 18:10:26.514748	2026-01-06 18:10:26.514752	aureajanan@gmail.com	71988089669	t	\N	\N	\N	\N		(71) 98612-1321	40749-045	Rua 22 de Março	150	Salvador	1
9	Marelene Costa Silva	58018921504	1968-04-03	2026-01-06 18:16:36.289753	2026-01-06 18:16:36.289756	mcs-100@hotmail.com	71993103741	t	\N	\N	\N	\N		(71) 99327-5505	40732-075	Rua 15 de Novembro	116	Salvador	1
10	Soraia de Paula Oliveira	86087940553	1973-03-27	2026-01-06 18:22:09.382397	2026-01-06 18:22:09.382401	soraiadepaula7@gmail.com	71983615291	t	\N	\N	\N	\N		(71) 98514-8008	40748-535	2ª Travessa Alto Cerqueira	26	Salvador	1
11	Prisciliana Fernandes Pantoja	82422281591	1982-01-20	2026-01-06 18:26:25.240787	2026-01-06 18:26:25.240792	priscilianapantoja@gmail.com	71988160327	t	\N	\N	\N	\N		(71) 98719-2201	40749-025	Travessa 16	230	Salvador	1
\.


--
-- Name: activities_id_seq; Type: SEQUENCE SET; Schema: academy; Owner: natan33
--

SELECT pg_catalog.setval('academy.activities_id_seq', 11, true);


--
-- Name: attendance_id_seq; Type: SEQUENCE SET; Schema: academy; Owner: natan33
--

SELECT pg_catalog.setval('academy.attendance_id_seq', 7, true);


--
-- Name: attendance_summary_id_seq; Type: SEQUENCE SET; Schema: academy; Owner: natan33
--

SELECT pg_catalog.setval('academy.attendance_summary_id_seq', 1, false);


--
-- Name: class_schedule_id_seq; Type: SEQUENCE SET; Schema: academy; Owner: natan33
--

SELECT pg_catalog.setval('academy.class_schedule_id_seq', 48, true);


--
-- Name: enrollments_id_seq; Type: SEQUENCE SET; Schema: academy; Owner: natan33
--

SELECT pg_catalog.setval('academy.enrollments_id_seq', 25, true);


--
-- Name: modalities_id_seq; Type: SEQUENCE SET; Schema: academy; Owner: natan33
--

SELECT pg_catalog.setval('academy.modalities_id_seq', 1, false);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: core; Owner: natan33
--

SELECT pg_catalog.setval('core.audit_logs_id_seq', 1, false);


--
-- Name: settings_id_seq; Type: SEQUENCE SET; Schema: core; Owner: natan33
--

SELECT pg_catalog.setval('core.settings_id_seq', 1, false);


--
-- Name: welcome_email_logs_id_seq; Type: SEQUENCE SET; Schema: core; Owner: natan33
--

SELECT pg_catalog.setval('core.welcome_email_logs_id_seq', 11, true);


--
-- Name: expenses_id_seq; Type: SEQUENCE SET; Schema: finance; Owner: natan33
--

SELECT pg_catalog.setval('finance.expenses_id_seq', 9, true);


--
-- Name: invoices_id_seq; Type: SEQUENCE SET; Schema: finance; Owner: natan33
--

SELECT pg_catalog.setval('finance.invoices_id_seq', 34, true);


--
-- Name: plans_id_seq; Type: SEQUENCE SET; Schema: finance; Owner: natan33
--

SELECT pg_catalog.setval('finance.plans_id_seq', 6, true);


--
-- Name: registrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: natan33
--

SELECT pg_catalog.setval('public.registrations_id_seq', 3, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: natan33
--

SELECT pg_catalog.setval('public.users_id_seq', 3, true);


--
-- Name: student_health_data_id_seq; Type: SEQUENCE SET; Schema: students; Owner: natan33
--

SELECT pg_catalog.setval('students.student_health_data_id_seq', 10, true);


--
-- Name: students_id_seq; Type: SEQUENCE SET; Schema: students; Owner: natan33
--

SELECT pg_catalog.setval('students.students_id_seq', 11, true);


--
-- Name: activities activities_name_key; Type: CONSTRAINT; Schema: academy; Owner: natan33
--

ALTER TABLE ONLY academy.activities
    ADD CONSTRAINT activities_name_key UNIQUE (name);


--
-- Name: activities activities_pkey; Type: CONSTRAINT; Schema: academy; Owner: natan33
--

ALTER TABLE ONLY academy.activities
    ADD CONSTRAINT activities_pkey PRIMARY KEY (id);


--
-- Name: attendance attendance_pkey; Type: CONSTRAINT; Schema: academy; Owner: natan33
--

ALTER TABLE ONLY academy.attendance
    ADD CONSTRAINT attendance_pkey PRIMARY KEY (id);


--
-- Name: attendance_summary attendance_summary_pkey; Type: CONSTRAINT; Schema: academy; Owner: natan33
--

ALTER TABLE ONLY academy.attendance_summary
    ADD CONSTRAINT attendance_summary_pkey PRIMARY KEY (id);


--
-- Name: class_schedule class_schedule_pkey; Type: CONSTRAINT; Schema: academy; Owner: natan33
--

ALTER TABLE ONLY academy.class_schedule
    ADD CONSTRAINT class_schedule_pkey PRIMARY KEY (id);


--
-- Name: class_students class_students_pkey; Type: CONSTRAINT; Schema: academy; Owner: natan33
--

ALTER TABLE ONLY academy.class_students
    ADD CONSTRAINT class_students_pkey PRIMARY KEY (student_id, class_id);


--
-- Name: enrollments enrollments_pkey; Type: CONSTRAINT; Schema: academy; Owner: natan33
--

ALTER TABLE ONLY academy.enrollments
    ADD CONSTRAINT enrollments_pkey PRIMARY KEY (id);


--
-- Name: modalities modalities_pkey; Type: CONSTRAINT; Schema: academy; Owner: natan33
--

ALTER TABLE ONLY academy.modalities
    ADD CONSTRAINT modalities_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: core; Owner: natan33
--

ALTER TABLE ONLY core.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: settings settings_key_key; Type: CONSTRAINT; Schema: core; Owner: natan33
--

ALTER TABLE ONLY core.settings
    ADD CONSTRAINT settings_key_key UNIQUE (key);


--
-- Name: settings settings_pkey; Type: CONSTRAINT; Schema: core; Owner: natan33
--

ALTER TABLE ONLY core.settings
    ADD CONSTRAINT settings_pkey PRIMARY KEY (id);


--
-- Name: welcome_email_logs welcome_email_logs_pkey; Type: CONSTRAINT; Schema: core; Owner: natan33
--

ALTER TABLE ONLY core.welcome_email_logs
    ADD CONSTRAINT welcome_email_logs_pkey PRIMARY KEY (id);


--
-- Name: welcome_email_logs welcome_email_logs_student_id_key; Type: CONSTRAINT; Schema: core; Owner: natan33
--

ALTER TABLE ONLY core.welcome_email_logs
    ADD CONSTRAINT welcome_email_logs_student_id_key UNIQUE (student_id);


--
-- Name: expenses expenses_pkey; Type: CONSTRAINT; Schema: finance; Owner: natan33
--

ALTER TABLE ONLY finance.expenses
    ADD CONSTRAINT expenses_pkey PRIMARY KEY (id);


--
-- Name: invoices invoices_pkey; Type: CONSTRAINT; Schema: finance; Owner: natan33
--

ALTER TABLE ONLY finance.invoices
    ADD CONSTRAINT invoices_pkey PRIMARY KEY (id);


--
-- Name: plans plans_pkey; Type: CONSTRAINT; Schema: finance; Owner: natan33
--

ALTER TABLE ONLY finance.plans
    ADD CONSTRAINT plans_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: natan33
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: registrations registrations_pkey; Type: CONSTRAINT; Schema: public; Owner: natan33
--

ALTER TABLE ONLY public.registrations
    ADD CONSTRAINT registrations_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: natan33
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: student_health_data student_health_data_pkey; Type: CONSTRAINT; Schema: students; Owner: natan33
--

ALTER TABLE ONLY students.student_health_data
    ADD CONSTRAINT student_health_data_pkey PRIMARY KEY (id);


--
-- Name: students students_email_key; Type: CONSTRAINT; Schema: students; Owner: natan33
--

ALTER TABLE ONLY students.students
    ADD CONSTRAINT students_email_key UNIQUE (email);


--
-- Name: students students_pkey; Type: CONSTRAINT; Schema: students; Owner: natan33
--

ALTER TABLE ONLY students.students
    ADD CONSTRAINT students_pkey PRIMARY KEY (id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: natan33
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: natan33
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: ix_students_students_cpf; Type: INDEX; Schema: students; Owner: natan33
--

CREATE UNIQUE INDEX ix_students_students_cpf ON students.students USING btree (cpf);


--
-- Name: attendance attendance_schedule_id_fkey; Type: FK CONSTRAINT; Schema: academy; Owner: natan33
--

ALTER TABLE ONLY academy.attendance
    ADD CONSTRAINT attendance_schedule_id_fkey FOREIGN KEY (schedule_id) REFERENCES academy.class_schedule(id);


--
-- Name: attendance attendance_student_id_fkey; Type: FK CONSTRAINT; Schema: academy; Owner: natan33
--

ALTER TABLE ONLY academy.attendance
    ADD CONSTRAINT attendance_student_id_fkey FOREIGN KEY (student_id) REFERENCES students.students(id);


--
-- Name: attendance_summary attendance_summary_student_id_fkey; Type: FK CONSTRAINT; Schema: academy; Owner: natan33
--

ALTER TABLE ONLY academy.attendance_summary
    ADD CONSTRAINT attendance_summary_student_id_fkey FOREIGN KEY (student_id) REFERENCES students.students(id);


--
-- Name: class_schedule class_schedule_activity_id_fkey; Type: FK CONSTRAINT; Schema: academy; Owner: natan33
--

ALTER TABLE ONLY academy.class_schedule
    ADD CONSTRAINT class_schedule_activity_id_fkey FOREIGN KEY (activity_id) REFERENCES academy.activities(id);


--
-- Name: class_students class_students_class_id_fkey; Type: FK CONSTRAINT; Schema: academy; Owner: natan33
--

ALTER TABLE ONLY academy.class_students
    ADD CONSTRAINT class_students_class_id_fkey FOREIGN KEY (class_id) REFERENCES academy.class_schedule(id);


--
-- Name: class_students class_students_student_id_fkey; Type: FK CONSTRAINT; Schema: academy; Owner: natan33
--

ALTER TABLE ONLY academy.class_students
    ADD CONSTRAINT class_students_student_id_fkey FOREIGN KEY (student_id) REFERENCES students.students(id);


--
-- Name: enrollments enrollments_schedule_id_fkey; Type: FK CONSTRAINT; Schema: academy; Owner: natan33
--

ALTER TABLE ONLY academy.enrollments
    ADD CONSTRAINT enrollments_schedule_id_fkey FOREIGN KEY (schedule_id) REFERENCES academy.class_schedule(id);


--
-- Name: enrollments enrollments_student_id_fkey; Type: FK CONSTRAINT; Schema: academy; Owner: natan33
--

ALTER TABLE ONLY academy.enrollments
    ADD CONSTRAINT enrollments_student_id_fkey FOREIGN KEY (student_id) REFERENCES students.students(id);


--
-- Name: audit_logs audit_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: natan33
--

ALTER TABLE ONLY core.audit_logs
    ADD CONSTRAINT audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: welcome_email_logs welcome_email_logs_student_id_fkey; Type: FK CONSTRAINT; Schema: core; Owner: natan33
--

ALTER TABLE ONLY core.welcome_email_logs
    ADD CONSTRAINT welcome_email_logs_student_id_fkey FOREIGN KEY (student_id) REFERENCES students.students(id);


--
-- Name: invoices invoices_plan_id_fkey; Type: FK CONSTRAINT; Schema: finance; Owner: natan33
--

ALTER TABLE ONLY finance.invoices
    ADD CONSTRAINT invoices_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES finance.plans(id);


--
-- Name: invoices invoices_student_id_fkey; Type: FK CONSTRAINT; Schema: finance; Owner: natan33
--

ALTER TABLE ONLY finance.invoices
    ADD CONSTRAINT invoices_student_id_fkey FOREIGN KEY (student_id) REFERENCES students.students(id);


--
-- Name: registrations registrations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: natan33
--

ALTER TABLE ONLY public.registrations
    ADD CONSTRAINT registrations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: student_health_data student_health_data_student_id_fkey; Type: FK CONSTRAINT; Schema: students; Owner: natan33
--

ALTER TABLE ONLY students.student_health_data
    ADD CONSTRAINT student_health_data_student_id_fkey FOREIGN KEY (student_id) REFERENCES students.students(id);


--
-- Name: students students_plan_id_fkey; Type: FK CONSTRAINT; Schema: students; Owner: natan33
--

ALTER TABLE ONLY students.students
    ADD CONSTRAINT students_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES finance.plans(id);


--
-- Name: SCHEMA academy; Type: ACL; Schema: -; Owner: postgres
--

GRANT ALL ON SCHEMA academy TO natan33;


--
-- Name: SCHEMA core; Type: ACL; Schema: -; Owner: postgres
--

GRANT ALL ON SCHEMA core TO natan33;


--
-- Name: SCHEMA finance; Type: ACL; Schema: -; Owner: postgres
--

GRANT ALL ON SCHEMA finance TO natan33;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO natan33;


--
-- Name: SCHEMA students; Type: ACL; Schema: -; Owner: postgres
--

GRANT ALL ON SCHEMA students TO natan33;


--
-- PostgreSQL database dump complete
--

\unrestrict NLHxhs7TPPmK0y5ifGNj5i318XgAEH538MpARcpPf0hP55HLAg79TaRGmSphQyG

