from vector_store.consumer_vector_store import search_consumer_law
from vector_store.cybercrime_vector_store import search_cyber_law
from agents.similar_case_agent import get_similar_cases
from agents.case_law_agent import retrieve_case_law


def route_retrieval(query, domain):

    ipc_sections = []
    consumer_laws = []
    cyber_laws = []
    case_laws = retrieve_case_law(query)

    if domain == "criminal":
        ipc_sections = get_similar_cases(query)

    elif domain == "consumer":
        consumer_laws = search_consumer_law(query)

    elif domain == "cybercrime":
        cyber_laws = search_cyber_law(query)

    return ipc_sections, consumer_laws, cyber_laws, case_laws