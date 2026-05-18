<!-- HOOK -->

*"This awful language has escaped the browser and infiltrated our servers."* That was a Hacker News commenter, writing about JavaScript in 2014. It has never been the most loved language — but in 2026, it runs the world's infrastructure. So how did it get here?

<!-- BODY -->

The story of how this happened has four questions. Each one is a door JavaScript walked through. And every door opened the same way.

*Why did we have JavaScript at all?*

In May 1995, Netscape needed a scripting language for the browser. Java was too heavy — it required a virtual machine, a class file format, a separate runtime download. C was unthinkable. They needed something a webpage author — a designer, a marketer, an intern — could actually write. So they hired a thirty-three-year-old engineer named Brendan Eich and gave him a deadline. He shipped a working prototype in ten days. They called it Mocha. By September it was LiveScript. By December — in a joint announcement with Sun Microsystems — it was JavaScript. The name was a marketing move. The language has nothing to do with Java. But the name stuck. And every browser shipped with it. Every browser. Every webpage. Every device that talks to the web.

JavaScript wasn't designed to win. It was designed to be available. Those are different things.

*How did JavaScript get to the server?*

For fourteen years, it didn't. The server ran Perl, then PHP, then Python, then Ruby. JavaScript lived inside the browser, and most people thought it would die there.

But in November 2009, an engineer named Ryan Dahl walked onto a stage in Berlin in front of 150 people. He'd been watching Apache choke under concurrent connections. Every request opened a new thread. Every thread ate memory. The server collapsed when too many users showed up at once. He wanted something different — a server that didn't block. And he chose JavaScript for a very specific reason. Every other language already had an I/O library built around blocking. Ruby had EventMachine. Python had Twisted. Both were fighting their own language's defaults. JavaScript had no I/O library at all. And JavaScript developers were the only programmers on Earth who already thought in events — because that's how the browser works, and that's where they'd spent their whole careers. He took V8, wrapped it in an event loop, and turned it into a server runtime. He called it Node.js. The audience gave him a standing ovation — the first in the conference's history.

Within months, tens of thousands of engineers were running it.

JavaScript had escaped the browser.

And there's the line. A Hacker News commenter, writing in 2014, used exactly that verb. *We allowed this awful language to escape the browser and infiltrate our servers in form of Node.js.* He was right about the escape. But he didn't know what was coming next.

*How did JavaScript get to mobile and desktop?*

GitHub went first. In 2013, an engineer at GitHub named Cheng Zhao wrapped Chromium and Node.js into a single runtime. GitHub was building a text editor called Atom — and Atom's pitch was the hackable editor, customizable in the same language its users wrote every day. For most of them, that meant JavaScript. So Atom had to ship with a browser inside it. The runtime was called Atom Shell. Two years later, GitHub renamed it Electron.

Then Facebook moved. In 2012, Mark Zuckerberg had called Facebook's HTML5 mobile bet *the biggest mistake we've made as a company*. They scrapped it and rebuilt native — iOS and Android, separately. Two codebases, twice the cost. In 2013, an engineer named Jordan Walke proved at an internal hackathon that React's component model could drive real native UI on iOS. Not a webview. Actual native widgets. Same JavaScript code, two mobile platforms. Facebook open-sourced it at F8 in March 2015 and called it React Native. Then three platforms. Then everything.

By the time anyone really noticed, the apps on our screens weren't apps anymore. They were browsers wearing app costumes. VS Code is Electron. Slack is Electron. Discord, Figma, Notion, 1Password, Obsidian — all Electron. Your code editor is a browser. Your password manager is a browser. Your favorite chat app is a browser too.

*How did JavaScript take over the world?*

By being the language that was already there.

But the moment the takeover became literal — the moment we should pin in our memory — is this one. In 2024, Microsoft confirmed that part of the Windows 11 Start menu was built with React Native. The interface rendered into the native XAML layer underneath. Not a webview pretending to be native. Actual native UI controls, described in JavaScript. And Microsoft made this choice on purpose. The "recommended" section pulls personalized files, recent apps, frequently-changing content. It needed to ship fast and iterate fast — faster than recompiling Windows could allow. So Microsoft built and maintains its own fork, React Native for Windows, specifically so JavaScript can drive native Windows widgets. The most-deployed operating system on the planet was drawing its own menu in the language one engineer wrote in ten days. The 2014 commenter had imagined Node.js as a virus escaping a quarantine zone. By 2024, that virus was drawing the Start menu of Windows.

And the substrate is still compounding. In 2026, every large language model on the market appears to have been trained on code corpora where JavaScript dominates. That means GitHub's public repos. Every npm package. Every blog post and answered Stack Overflow question. The most-trained-on language becomes the most-generated, the most-generated becomes the most-shipped, and the most-shipped becomes the next training corpus for the model after that. Stack Overflow's 2025 developer survey asked forty-nine thousand engineers what they actually use. JavaScript came in first — as it has every year for over a decade. Sixty-six percent. The single most-used language on the planet.

JavaScript didn't win on quality. It won on supply. The kid Netscape hired to write a scripting language in ten days, now writes the world.

<!-- LANDING -->

The next time you open your code editor, your password manager, or even the Start menu of Windows — remember you're running JavaScript. Not because it won. Because it was already there.
