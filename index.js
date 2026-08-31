const { Client, GatewayIntentBits, SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const { minecraftServerUtil } = require('minecraft-server-util');
require('dotenv').config();

const client = new Client({ intents: [GatewayIntentBits.Guilds] });

const MINECRAFT_IP = process.env.MINECRAFT_SERVER_IP;
const MINECRAFT_PORT = process.env.MINECRAFT_SERVER_PORT || 25565;
const CHANNEL_ID = process.env.DISCORD_CHANNEL_ID;

client.once('ready', () => {
  console.log(`✅ Bot logged in as ${client.user.tag}`);
});

client.on('interactionCreate', async (interaction) => {
  if (!interaction.isChatInputCommand()) return;

  const { commandName } = interaction;

  try {
    if (commandName === 'status') {
      await interaction.deferReply();
      
      try {
        const result = await minecraftServerUtil.status(MINECRAFT_IP, MINECRAFT_PORT);
        
        const embed = new EmbedBuilder()
          .setColor('#2ECC71')
          .setTitle('🎮 Minecraft Server Status')
          .addFields(
            { name: 'Server', value: `${MINECRAFT_IP}:${MINECRAFT_PORT}`, inline: true },
            { name: 'Status', value: '🟢 Online', inline: true },
            { name: 'Players', value: `${result.players.online}/${result.players.max}`, inline: true },
            { name: 'Version', value: result.version.name || 'Unknown', inline: true }
          )
          .setTimestamp();

        if (result.players.online > 0) {
          embed.addFields({
            name: 'Online Players',
            value: result.players.sample?.map(p => p.name).join(', ') || 'N/A'
          });
        }

        await interaction.editReply({ embeds: [embed] });
      } catch (error) {
        const errorEmbed = new EmbedBuilder()
          .setColor('#E74C3C')
          .setTitle('🎮 Minecraft Server Status')
          .addFields(
            { name: 'Server', value: `${MINECRAFT_IP}:${MINECRAFT_PORT}`, inline: true },
            { name: 'Status', value: '🔴 Offline' }
          )
          .setTimestamp();

        await interaction.editReply({ embeds: [errorEmbed] });
      }
    }
  } catch (error) {
    console.error(error);
    await interaction.reply({ content: 'An error occurred!', ephemeral: true });
  }
});

client.on('ready', async () => {
  try {
    const statusCommand = new SlashCommandBuilder()
      .setName('status')
      .setDescription('Check Minecraft server status');

    await client.application.commands.create(statusCommand);
    console.log('✅ Slash commands registered');
  } catch (error) {
    console.error('Failed to register commands:', error);
  }
});

client.login(process.env.DISCORD_TOKEN);
