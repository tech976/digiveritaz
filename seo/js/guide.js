/* Plain-English layer.
   The engine reports findings in SEO terms ("canonical", "Flesch", "keyphrase
   density"). This maps every check id to language someone with no SEO
   background can act on: what it means, why it costs money, what to do.

   cat    which section of the report it belongs to
   plain  the human name (shown by default; technical name shown in Expert mode)
   why    the business reason, in one sentence, no jargon
   fix    the concrete next action
   impact 3 = fix first, 1 = nice to have. Drives the "Fix these first" order. */
window.DV_GUIDE = {

  categories: [
    { id: "found",   title: "Can Google find and trust this page?",
      blurb: "The plumbing. If any of this is broken, nothing else you do will help." },
    { id: "listing", title: "How it looks in Google results",
      blurb: "The headline and description searchers actually see before they click." },
    { id: "match",   title: "Does it match what people search for?",
      blurb: "Whether the page actually talks about the thing you want to be found for." },
    { id: "content", title: "Is there enough on the page?",
      blurb: "Depth, structure, images and links — what makes a page worth ranking." },
    { id: "reading", title: "Is it easy to read?",
      blurb: "Hard-to-read pages lose visitors, and visitors leaving fast hurts rankings." },
  ],

  checks: {
    /* ---------------------------------------------------------- plumbing */
    http: { cat:"found", impact:3, plain:"The page loads",
      why:"If a page doesn't load, nothing else matters — Google can't read it and customers can't buy from it.",
      fix:"Send this URL to your developer. It isn't returning a normal 'OK' response." },

    indexable: { cat:"found", impact:3, plain:"Google is allowed to list it",
      why:"A page can carry a hidden instruction telling Google to ignore it. Set by accident, the page can never appear in search no matter how good it is.",
      fix:"Remove the 'noindex' instruction from this page." },

    canonical: { cat:"found", impact:2, plain:"No duplicate-address confusion",
      why:"The same page can usually be reached at several slightly different web addresses. Without a tag naming the official one, Google splits your credit between them and every version ranks worse.",
      fix:"Add a canonical tag naming the one address you want Google to use." },

    viewport: { cat:"found", impact:3, plain:"Works properly on phones",
      why:"Most of your visitors are on a phone, and Google judges your site by its phone version. Without this the page loads desktop-sized and unreadable.",
      fix:"Add the mobile viewport tag to the page." },

    lang: { cat:"found", impact:1, plain:"Language is declared",
      why:"Tells Google which language and country the page is written for, so it shows to the right audience.",
      fix:"Add a language attribute such as en-IN or en-GB to the page." },

    schema: { cat:"found", impact:2, plain:"Extra details for Google",
      why:"A hidden summary that lets Google show your listing with FAQs, ratings or business details instead of a plain blue link. Richer listings get more clicks.",
      fix:"Add structured data describing what this page is — a service, an article, a business." },

    open_graph: { cat:"found", impact:2, plain:"Looks right when shared",
      why:"When someone pastes your link into WhatsApp or LinkedIn, these tags decide the image and headline that appear. Without them the link looks bare and gets ignored.",
      fix:"Add sharing tags for the title, description and a preview image." },

    twitter: { cat:"found", impact:1, plain:"Looks right when shared on X",
      why:"The same preview, for X/Twitter. Small, but free to fix.",
      fix:"Add a Twitter card tag." },

    /* ------------------------------------------------ the Google listing */
    title_width: { cat:"listing", impact:3, plain:"Headline fits in Google",
      why:"Your headline is the biggest, most clicked text in the search result. Too long and Google chops it off mid-word; too short and you waste prime advertising space.",
      fix:"Aim for roughly 50–60 characters — long enough to fill the space, short enough not to be cut." },

    meta_desc: { cat:"listing", impact:3, plain:"Description fits in Google",
      why:"This is the sales pitch under your headline. If it's missing, Google grabs a random sentence from the page instead — usually a bad one.",
      fix:"Write 120–156 characters that give someone a reason to click." },

    /* ----------------------------------------------------- search intent */
    keyphrase_set: { cat:"match", impact:2, plain:"A target phrase is set",
      why:"Each page should aim at one thing people actually type into Google. Without one, there's nothing to measure the page against.",
      fix:"Set the phrase you want this page to be found for, using the box at the top of this report." },

    keyphrase_length: { cat:"match", impact:1, plain:"Target phrase is a sensible length",
      why:"Very long phrases are searched for by almost nobody, so ranking for one wins you little.",
      fix:"Aim for two to four words." },

    title_keyphrase: { cat:"match", impact:3, plain:"Target phrase in the headline",
      why:"The headline is the strongest clue Google has about what a page is for. If your phrase isn't in it, you are unlikely to rank for that phrase at all.",
      fix:"Work the phrase into the headline, as close to the start as reads naturally." },

    meta_keyphrase: { cat:"match", impact:2, plain:"Target phrase in the description",
      why:"Google bolds the searcher's words in the description. Seeing their own phrase back makes people far more likely to click.",
      fix:"Include the phrase once in the description, written for a human." },

    slug_keyphrase: { cat:"match", impact:2, plain:"Target phrase in the web address",
      why:"A clear address helps both Google and anyone deciding whether the link is worth clicking.",
      fix:"Only worth changing on a new page — renaming a live address needs a redirect, so check with your developer first." },

    intro_keyphrase: { cat:"match", impact:2, plain:"Target phrase in the opening lines",
      why:"Readers and Google both decide what a page is about within the first paragraph. Leave the phrase out and both may decide it's about something else.",
      fix:"Rewrite the opening so the phrase appears naturally in the first few lines." },

    subhead_keyphrase: { cat:"match", impact:2, plain:"Target phrase in the section headings",
      why:"Headings are the skeleton of the page. Using the phrase in one or two confirms the whole page is genuinely about that topic.",
      fix:"Work the phrase into at least one section heading — but don't force it into all of them." },

    density: { cat:"match", impact:3, plain:"Phrase used the right number of times",
      why:"Mention it too rarely and the page reads as being about something else. Mention it too often and Google treats it as spam.",
      fix:"Aim for the phrase to make up roughly 0.5% to 3% of the words on the page." },

    alt_keyphrase: { cat:"match", impact:1, plain:"Target phrase in an image description",
      why:"Image descriptions are one more honest place to reinforce the topic, and they feed Google Images too.",
      fix:"Mention the phrase in the description of the one image it genuinely describes." },

    /* ---------------------------------------------------------- content */
    text_length: { cat:"content", impact:3, plain:"Enough content to be useful",
      why:"Thin pages rarely rank, because a competitor with a fuller answer will outrank them every time.",
      fix:"Aim for 600+ words on a page meant to win business — answering real customer questions, not padding." },

    h1: { cat:"content", impact:3, plain:"One clear main heading",
      why:"The main heading tells the reader in one line what the page is. Having none is confusing; having several is like a book with three titles.",
      fix:"Give the page exactly one main heading." },

    heading_order: { cat:"content", impact:1, plain:"Headings are properly nested",
      why:"Headings should step down in order, like chapter and section. Skipping levels makes the page harder to follow, especially for screen readers.",
      fix:"Don't jump from a main heading straight to a small sub-sub-heading." },

    img_alt: { cat:"content", impact:2, plain:"Images have descriptions",
      why:"Blind visitors rely on these, and Google can't see pictures either. Missing descriptions is both an accessibility and a search problem.",
      fix:"Add a short, literal description to every meaningful image." },

    internal_links: { cat:"content", impact:2, plain:"Links to your other pages",
      why:"Links between your own pages pass authority around and guide visitors to the next step. An unlinked page is a dead end.",
      fix:"Add a few relevant links to related pages on your site." },

    outbound_links: { cat:"content", impact:1, plain:"Links to trustworthy sources",
      why:"Citing a credible source signals your content is researched rather than invented.",
      fix:"Link out once or twice to a genuinely authoritative source." },

    /* -------------------------------------------------------- readability */
    flesch: { cat:"reading", impact:3, plain:"Plain enough to read easily",
      why:"Dense writing makes people leave, and people leaving quickly tells Google the page didn't answer the question.",
      fix:"Shorter sentences and simpler words. Say 'use' instead of 'utilise', and split long sentences in two." },

    sentence_length: { cat:"reading", impact:2, plain:"Sentences aren't too long",
      why:"Long sentences are hard to follow on a phone, which is where most people will read this.",
      fix:"Break sentences longer than about 20 words into two." },

    paragraph_length: { cat:"reading", impact:2, plain:"Paragraphs aren't walls of text",
      why:"A big unbroken block of text makes people scroll past instead of reading.",
      fix:"Keep paragraphs under about 150 words — three or four sentences." },

    subheading_distribution: { cat:"reading", impact:2, plain:"Broken up with headings",
      why:"Most people scan rather than read. Long stretches with no heading give them nothing to scan, so they give up.",
      fix:"Add a heading every 300 words or so." },

    passive_voice: { cat:"reading", impact:1, plain:"Written in a direct voice",
      why:"'The campaign was managed by our team' is weaker and longer than 'our team managed the campaign'.",
      fix:"Rewrite sentences so the person doing the action comes first." },

    transition_words: { cat:"reading", impact:1, plain:"Ideas flow together",
      why:"Words like 'however', 'because' and 'as a result' show readers how your points connect, instead of leaving a list of disconnected facts.",
      fix:"Add linking words between sentences where the logic needs signposting." },

    consecutive: { cat:"reading", impact:1, plain:"Sentences don't all start the same way",
      why:"Several sentences opening with the same word reads as monotonous and makes people switch off.",
      fix:"Vary how sentences begin." },
  },

  /* One-line verdicts, in plain language. */
  verdict(score){
    if (score == null)  return { word:"Not checked yet", line:"Run the check to see how this page is doing." };
    if (score >= 85)    return { word:"Good",        line:"This page is in good shape. Only small refinements left." };
    if (score >= 70)    return { word:"Nearly there",line:"Solid foundations, but a few fixable things are holding it back." };
    if (score >= 55)    return { word:"Needs work",  line:"This page works, but it's leaving real traffic on the table." };
    return                     { word:"Poor",        line:"This page has problems that are actively costing you visitors." };
  },

  siteVerdict(score, pages){
    if (score == null) return "Press “Check my site” to see how your pages are doing.";
    const v = this.verdict(score).word.toLowerCase();
    return `Across ${pages} page${pages !== 1 ? "s" : ""}, your site scores ${score} out of 100 — ${v}. `
         + `The list below is ordered by what will make the biggest difference.`;
  },
};
