/* 

Return distribution of most common scores for Wordle puzzles 

*/

-- There is a bug causing some all zeros will fix later but now just patch it
delete from wordle_records where distribution = '{0,0,0,0,0,0,0}';


-- Pandas dataframe to_sql do not create array column but text in {1,2,3} format 
-- I might have to create the schema first then write the array in order to achieve that
-- So here I will use a hacky way to split string to array

with parsed as (
select
	puzzle_number, dt,
	string_to_array(regexp_replace(distribution, '[{}]', '', 'g'), ',') distribution_array
	from wordle_records
	-- where dt = '2022-06-11'
), unnested as (
select puzzle_number, dt, cast(a.perc as int), trials -- Must case as int to sort correctly
from parsed
left join lateral unnest(parsed.distribution_array)
WITH ORDINALITY AS a(perc, trials) ON true
), ranked as (
select
	*,
	row_number() over (
		partition by puzzle_number
		order by perc desc 
	) as rnk
from unnested),
grouped as (
select 
	trials, count(*) cnt,
	array_agg(dt) -- Use to spot check
from ranked 
where rnk = 1
group by 1
order by 2 desc
)
select 
	trials, cnt,
	100* cnt/ sum(cnt) over() as perc
from grouped;
