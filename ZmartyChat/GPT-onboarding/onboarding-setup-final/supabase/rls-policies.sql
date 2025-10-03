CREATE POLICY test_policy ON auth.users FOR SELECT USING (auth.uid() = id);
