DROP TABLE computers_computernewclass;
DROP TABLE config_baculasettings;
ALTER TABLE procedures_procedure ALTER COLUMN pool_size TYPE bigint;

-- Name: procedures_procedure_job_tasks; Type: TABLE; Schema: public; Owner: nimbus; Tablespace: 
--

CREATE TABLE procedures_procedure_job_tasks (
    id integer NOT NULL,
    procedure_id integer NOT NULL,
    jobtask_id integer NOT NULL
);


ALTER TABLE public.procedures_procedure_job_tasks OWNER TO nimbus;

--
-- Name: procedures_procedure_job_tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: nimbus
--

CREATE SEQUENCE procedures_procedure_job_tasks_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.procedures_procedure_job_tasks_id_seq OWNER TO nimbus;

--
-- Name: procedures_procedure_job_tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nimbus
--

ALTER SEQUENCE procedures_procedure_job_tasks_id_seq OWNED BY procedures_procedure_job_tasks.id;


ALTER TABLE procedures_procedure_job_tasks ALTER COLUMN id SET DEFAULT nextval('procedures_procedure_job_tasks_id_seq'::regclass);


-- Name: procedures_procedure_job_tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: nimbus; Tablespace: 
--

ALTER TABLE ONLY procedures_procedure_job_tasks
    ADD CONSTRAINT procedures_procedure_job_tasks_pkey PRIMARY KEY (id);


--
-- Name: procedures_procedure_job_tasks_procedure_id_key; Type: CONSTRAINT; Schema: public; Owner: nimbus; Tablespace: 
--

ALTER TABLE ONLY procedures_procedure_job_tasks
    ADD CONSTRAINT procedures_procedure_job_tasks_procedure_id_key UNIQUE (procedure_id, jobtask_id);


--- Name: procedures_procedure_job_tasks_jobtask_id; Type: INDEX; Schema: public; Owner: nimbus; Tablespace: 
--

CREATE INDEX procedures_procedure_job_tasks_jobtask_id ON procedures_procedure_job_tasks USING btree (jobtask_id);


--
-- Name: procedures_procedure_job_tasks_procedure_id; Type: INDEX; Schema: public; Owner: nimbus; Tablespace: 
--

CREATE INDEX procedures_procedure_job_tasks_procedure_id ON procedures_procedure_job_tasks USING btree (procedure_id);


-- Name: procedure_id_refs_id_48b2c082; Type: FK CONSTRAINT; Schema: public; Owner: nimbus
--

ALTER TABLE ONLY procedures_procedure_job_tasks
    ADD CONSTRAINT procedure_id_refs_id_48b2c082 FOREIGN KEY (procedure_id) REFERENCES procedures_procedure(id) DEFERRABLE INITIALLY DEFERRED;


-- Name: procedures_procedure_job_tasks_jobtask_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: nimbus
--

ALTER TABLE ONLY procedures_procedure_job_tasks
    ADD CONSTRAINT procedures_procedure_job_tasks_jobtask_id_fkey FOREIGN KEY (jobtask_id) REFERENCES procedures_jobtask(id) DEFERRABLE INITIALLY DEFERRED;


-
