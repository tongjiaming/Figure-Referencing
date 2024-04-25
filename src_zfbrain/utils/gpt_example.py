from dotenv import load_dotenv
import os

from openai import OpenAI

OPENAI_API_KEY=''

# load_dotenv()
# os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)

system_message = "You are a scientific assistant and your job is to identify the most appropriate figure or table to reference in a given sentence. Do not generate anything other than the label of the appropriate candidate. If none of the candidate figures and tables are appropriate, generate 'None of the above'. Do not go online."

query_paper_id = 'PMC8998009'

query_sentence = f"The results obtained after performing the experiments showed that the cell viability of the synbiotic microcapsules in the four types of yogurts was over 10 log10 cfu/g [FIGREF]."

label2caption = {
  'table_1': "The size and cell load of the microcapsules used.",
  'figure_1': "(A) Colonies of L. delbrueckii subsp. bulgaricus; (B) colonies of L. casei, L. rhamnosus and L. plantarum.",
  'figure_2': "Cell viability of oat milk yogurt samples. I M—yogurt without synbiotic microcapsules (control sample); I STH—yogurt containing synbiotic microcapsules with starch; I INU—yogurt containing synbiotic microcapsules with inulin; I G—yogurt containing microcapsules with glucose; I OLI—yogurt containing synbiotic microcapsules with oligofructose. T0 = the moment of analysis from the day of obtaining the yogurt; –T7, –T14, –T21 and –T28—yogurt analysis moments reported relative to day T0. Each bar presents the mean of three replicates ± standard deviation.",
  'table_2': "Physico-chemical and texture parameters of oat milk yogurt samples. Mean values and standard deviations.",
  'table_3': "Monitoring for color differences (ΔE) and opacity/brightness ΔC *.",
  'figure_3': "Evolution of viscoelastic parameters during the storage period of vegetable yogurt: (1) G′—modulus of elasticity, (2) G″—modulus of viscosity; (a)—control yogurt, without synbiotic microcapsules, (b)—yogurt containing microcapsules with glucose, (c)—yogurt containing synbiotic microcapsules with starch, (d)—yogurt containing synbiotic microcapsules with oligofructose, (e)—yogurt containing synbiotic microcapsules with inulin; T0—the moment of analysis from the day of obtaining the yogurt; T7, T14, T21 and T28—yogurt analysis moments relative to day T0.",
  'figure_4': "Sensory analysis of yogurt samples. Pmp—general acceptability; M—control yogurt, without synbiotic microcapsules; INU—yogurt containing synbiotic microcapsules with inulin; OLI—yogurt containing synbiotic microcapsules with oligofructose; STH—yogurt containing synbiotic microcapsules with starch; G—yogurt containing microcapsules with glucose; T0 = the moment of analysis from the day of obtaining the yogurt; –T7, –T14, –T21 and –T28—yogurt analysis moments reported relative to day T0.",
  'figure_5': "Profile of organic acids in oat milk yogurt samples. I M—yogurt without synbiotic microcapsules (control sample); I STH—yogurt containing synbiotic microcapsules with starch; I INU—yogurt containing synbiotic microcapsules with inulin; I G—yogurt containing microcapsules with glucose; I OLI—yogurt containing synbiotic microcapsules with oligofructose. T0 = the moment of analysis from the day of obtaining the yogurt; –T7, –T14, –T21 and –T28—yogurt analysis moments reported relative to day T0. Each bar presents the mean of three replicates ± standard deviation.",
  'figure_6': "Amino acid profile of oat milk yogurt samples. I M—yogurt without synbiotic microcapsules (control sample); I STH—yogurt containing synbiotic microcapsules with starch; I INU—yogurt containing synbiotic microcapsules with inulin; I G—yogurt containing microcapsules with glucose; I OLI—yogurt containing synbiotic microcapsules with oligofructose. T0 = the moment of analysis from the day of obtaining the yogurt; –T7, –T14, –T21 and –T28—yogurt analysis moments reported relative to day T0.",
  'figure_7': "Analysis of the main components—scores: T0–T28 M—yogurt control sample, analyzed from the moment of obtaining it to day 28 (T28); T0-T28 INU—yogurt sample with synbiotic microcapsules with inulin, analyzed from the moment of obtaining it to day 28 (T28); T0 OLI—yogurt sample with synbiotic microcapsules with oligofructose, analyzed from the moment of obtaining it to day 28 (T28); T0 STH—yogurt sample with synbiotic microcapsules with starch, analyzed from the moment of obtaining it to day 28 (T28); T0 G—yogurt sample with glucose microcapsules, analyzed from the moment of obtaining it to day 28 (T28).",
  'figure_8': "Analysis of the main components—influence of the parameters: pH; L*, a*, b*, dE*—total color difference; dC*—opaque/brightness difference; Acidity—titratable acidity; AciziOrgan—organic acids; A_Glu—gluconic acid; A_Lac—lactic acid; A_Ace—acetic acid; A_Suc—succinic acid; Acceptable—acceptability; Adhesiveness—adhesiveness; Cohesiveness—cohesiveness; Via_SG—cell viability in gastric juice; Via_SI—cell viability in intestinal juice; Via—cell viability in yogurt; Vasco—viscoelasticity; Duritate—hardness; adezivit—adhesivity; AromaOvaz—oat aroma; Vasco—viscosity; Aciditate—acidity; G′—elastic mode; G″—viscous mode; AAminop—α-aminopimelic acid; Ser—serine; Pro—proline; Asp—asparagine; Thi—thioproline; AAsp—aspartic acid; AGlu—glutamic acid; Ala—alanine; Gly—glycine; Val—valine; Leu—leucine; Glu—glutamine.",
}

concatenated_candidates = ''.join([
    f"- {label}: {caption}\n" for label, caption in label2caption.items()
])

user_message = f"""
I need to reference a figure or table at the position indicated by [FIGREF] in the following sentence:

{query_sentence}

Below are the labels and captions of all candidate figures and tables. Which should I reference?

{concatenated_candidates}
""".strip()

print(user_message)
completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": system_message},
    {"role": "user", "content": user_message},
  ]
)

print(completion.choices[0].message)
